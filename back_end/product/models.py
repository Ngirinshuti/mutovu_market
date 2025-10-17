from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.gis.db import models as gis_models
from django.utils import timezone
from cloudinary.models import CloudinaryField

class Category(models.Model):
    SIZE_TYPE_CHOICES = [
        ('numeric', 'Numeric (e.g., 32, 42)'),
        ('alpha', 'Alphabetic (e.g., S, M, L, XL)'),
        ('custom', 'Custom'),
    ]
    
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True, folder='product/categories/')
    size_type = models.CharField(max_length=10, choices=SIZE_TYPE_CHOICES, default='numeric',
                                help_text="Size type for all products in this category")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['category_name']
    
    def __str__(self):
        return str(self.category_name) if self.category_name else "Unnamed Category"

class SubCategory(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    subcategory_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True, folder='product/subcategories/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'SubCategory'
        verbose_name_plural = 'SubCategories'
        ordering = ['subcategory_name']
        unique_together = ['category', 'subcategory_name']
    
    def __str__(self):
        return f"{self.subcategory_name} ({self.category.category_name})" if self.subcategory_name else "Unnamed SubCategory"


class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    brand_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = CloudinaryField('image', blank=True, null=True, folder='product/brands/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['brand_name']
    
    def __str__(self):
        return str(self.brand_name) if self.brand_name else "Unnamed Brand"


class Size(models.Model):
    SIZE_TYPE_CHOICES = [
        ('numeric', 'Numeric (e.g., 32, 42)'),
        ('alpha', 'Alphabetic (e.g., S, M, L, XL)'),
        ('custom', 'Custom'),
    ]
    
    id = models.AutoField(primary_key=True)
    size_type = models.CharField(max_length=10, choices=SIZE_TYPE_CHOICES, default='numeric')
    numeric_size = models.PositiveIntegerField(blank=True, null=True)
    alpha_size = models.CharField(max_length=10, blank=True, null=True, 
                                  help_text="e.g., XS, S, M, L, XL, XXL")
    custom_size = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'
        ordering = ['size_type', 'numeric_size', 'alpha_size']
        unique_together = [
            ['size_type', 'numeric_size'],
            ['size_type', 'alpha_size'],
            ['size_type', 'custom_size']
        ]
    
    def clean(self):
        if self.size_type == 'numeric' and not self.numeric_size:
            raise ValidationError('Numeric size is required for numeric size type.')
        elif self.size_type == 'alpha' and not self.alpha_size:
            raise ValidationError('Alpha size is required for alphabetic size type.')
        elif self.size_type == 'custom' and not self.custom_size:
            raise ValidationError('Custom size is required for custom size type.')
    
    def __str__(self):
        if self.size_type == 'numeric' and self.numeric_size:
            return f"Size {self.numeric_size}"
        elif self.size_type == 'alpha' and self.alpha_size:
            return f"Size {self.alpha_size}"
        elif self.size_type == 'custom' and self.custom_size:
            return f"Size {self.custom_size}"
        return "Unnamed Size"


class Color(models.Model):
    id = models.AutoField(primary_key=True)
    color_name = models.CharField(max_length=100, unique=True)
    hex_code = models.CharField(max_length=7, blank=True, null=True, help_text="e.g., #FFFFFF")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'
        ordering = ['color_name']
    
    def __str__(self):
        return self.color_name if self.color_name else "Unnamed Color"


class Shop(models.Model):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True, verbose_name='ID')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='shops',
        help_text="The user who owns this shop"
    )
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    location = gis_models.PointField(
        srid=4326,
        blank=True,
        null=True,
        help_text="Geographic location (Point) of the shop (Longitude, Latitude)."
    )
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True, help_text="Whether the shop is currently active")
    is_verified = models.BooleanField(default=False, help_text="Whether the shop is verified by admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} (Owner: {self.owner.username})"
    
    @property
    def latitude(self):
        return self.location.y if self.location else None
    
    @property
    def longitude(self):
        return self.location.x if self.location else None


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=False, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=False, related_name='products')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField(blank=True, null=True, help_text="Detailed product description")
    
    available_sizes = models.ManyToManyField(Size, blank=True, related_name='products',
                                           help_text="All sizes available for this product")
    available_colors = models.ManyToManyField(Color, blank=True, related_name='products',
                                            help_text="All colors available for this product")
    is_active = models.BooleanField(default=True, help_text="Whether the product is available for sale")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']
    
    def __str__(self):
        return str(self.name) if self.name is not None else "Unnamed Product"
    
    def get_min_price(self):
        """Get minimum price among all active variants"""
        prices = self.variants.filter(is_active=True).values_list('price', flat=True)
        return float(min(prices)) if prices else 0.0

    def get_max_price(self):
        """Get maximum price among all active variants"""
        prices = self.variants.filter(is_active=True).values_list('price', flat=True)
        return float(max(prices)) if prices else 0.0

    def get_total_stock(self):
        """Get total stock across all active variants"""
        total = self.variants.filter(is_active=True).aggregate(
            total=models.Sum('quantity')
        )['total']
        return int(total) if total else 0

    def get_compatible_sizes(self):
        """Get sizes that are compatible with this product's category"""
        if self.category:
            return Size.objects.filter(size_type=self.category.size_type)
        return Size.objects.none()


class ProductImage(models.Model):
    """
    Centralized image model for product variants.
    Each image set (front, back, side, aerial) belongs to a specific variant.
    """
    id = models.AutoField(primary_key=True)
    variant = models.ForeignKey(
        'ProductVariant', 
        on_delete=models.CASCADE, 
        related_name='images',
        help_text="Product variant this image set belongs to"
    )
    front_image = CloudinaryField('front_image', blank=True, null=True, folder='product/variants/front/')
    back_image = CloudinaryField('back_image', blank=True, null=True, folder='product/variants/back/')
    side_image = CloudinaryField('side_image', blank=True, null=True, folder='product/variants/side/')
    aerial_image = CloudinaryField('aerial_image', blank=True, null=True, folder='product/variants/aerial/')
    
    is_primary = models.BooleanField(
        default=False,
        help_text="Primary image for this variant"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'
        ordering = ['-is_primary', '-created_at']
        indexes = [
            models.Index(fields=['variant', '-is_primary']),
        ]
    
    def __str__(self):
        return f"Image {self.id} - Variant {self.variant_id} {'[PRIMARY]' if self.is_primary else ''}"

    def clean(self):
        """Ensure at least one image is provided"""
        if not any([self.front_image, self.back_image, self.side_image, self.aerial_image]):
            raise ValidationError('At least one image must be provided.')
        
        # ADDED: Ensure variant is provided (not null)
        if not self.variant_id:
            raise ValidationError('Variant must be specified for images.')

class ProductVariant(models.Model):
    """
    Represents a specific combination of product + size + color.
    Each variant has its own stock, price, and images.
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True, related_name='product_variants')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True, related_name='product_variants')
    
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Price for this specific size/color combination"
    )
    quantity = models.PositiveIntegerField(
        default=0,
        help_text="Available quantity for this variant"
    )
    sku = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        unique=True,
        help_text="Stock Keeping Unit - unique identifier for this variant"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="Additional notes for this specific variant"
    )
    is_active = models.BooleanField(default=True, help_text="Whether this variant is available")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        unique_together = ['product', 'size', 'color']
        ordering = ['product__name', 'size__size_type', 'size__numeric_size', 'size__alpha_size', 'color__color_name']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        size_str = str(self.size) if self.size else 'No Size'
        color_str = str(self.color) if self.color else 'No Color'
        return f"{self.product.name} - {size_str}, {color_str} (${self.price}, Qty: {self.quantity})"

    def get_primary_image(self):
        """Get the primary image for this variant"""
        return self.images.filter(is_primary=True).first() or self.images.first()


class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='reviews',
        help_text="Review for specific variant (size/color combination)"
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ['product', 'user']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        variant_info = f" ({self.variant.size}, {self.variant.color})" if self.variant else ""
        return f"Review by {self.user.username} for {self.product.name}{variant_info} ({self.rating}★)"


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('returned', 'Returned'),
    ]
    DELIVERY_OPTION_CHOICES = [
        ('home_delivery', 'Home Delivery'),
        ('store_pickup', 'Store Pickup'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('flutterwave', 'Pay with Flutterwave'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Price per unit at time of order"
    )
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Total price for this order line"
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    
    delivery_option = models.CharField(max_length=20, choices=DELIVERY_OPTION_CHOICES, default='home_delivery')
    delivery_address = models.TextField(blank=True, null=True, help_text="Customer's delivery address")
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5.00, help_text="Delivery fee")
    estimated_delivery_time = models.PositiveIntegerField(blank=True, null=True, help_text="Estimated delivery time in minutes")
    deliverer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='deliveries',
        help_text="The user assigned to deliver this order"
    )
    
    recipient_name = models.CharField(max_length=255, blank=True, null=True)
    recipient_phone = models.CharField(max_length=50, blank=True, null=True)
    recipient_address_text = models.TextField(blank=True, null=True)
    recipient_address_lat = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    recipient_address_lng = models.DecimalField(max_digits=10, decimal_places=8, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash_on_delivery')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if self.unit_price and self.quantity:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    @property
    def product(self):
        return self.variant.product
    
    @property
    def size(self):
        return self.variant.size
    
    @property
    def color(self):
        return self.variant.color
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username} for {self.variant}"


class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['user', 'variant']
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['user', '-added_at']),
        ]
    
    def get_total_price(self):
        return self.variant.price * self.quantity
    
    @property
    def product(self):
        return self.variant.product
    
    @property
    def size(self):
        return self.variant.size
    
    @property
    def color(self):
        return self.variant.color
    
    def __str__(self):
        return f"CartItem: {self.quantity} of {self.variant} for {self.user.username}"


class WishlistItem(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    added_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = ['user', 'product']
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['user', '-added_at']),
        ]
    
    def __str__(self):
        return f"WishlistItem: {self.product.name} for {self.user.username}"


class Delivery(models.Model):
    DELIVERY_STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed Delivery'),
    ]
    
    id = models.AutoField(primary_key=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    deliverer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='assigned_deliveries'
    )
    pickup_address = models.TextField(help_text="Shop address for pickup")
    delivery_address = models.TextField(help_text="Customer address for delivery")
    pickup_time = models.DateTimeField(blank=True, null=True)
    delivery_time = models.DateTimeField(blank=True, null=True)
    estimated_time = models.PositiveIntegerField(help_text="Estimated delivery time in minutes")
    actual_time = models.PositiveIntegerField(blank=True, null=True, help_text="Actual delivery time in minutes")
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=5.00)
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, default='accepted')
    notes = models.TextField(blank=True, null=True, help_text="Delivery notes or instructions")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['deliverer', '-created_at']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Delivery #{self.id} - Order #{self.order.id} by {self.deliverer.username}"