from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.gis.db import models as gis_models

class Category(models.Model):
    SIZE_TYPE_CHOICES = [
        ('numeric', 'Numeric (e.g., 32, 42)'),
        ('alpha', 'Alphabetic (e.g., S, M, L, XL)'),
        ('custom', 'Custom'),
    ]
    
    id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='product/images/category_images/', blank=True, null=True)
    # Link size type to category - all products in this category will use this size type
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

class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    brand_name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='product/images/brand_images/', blank=True, null=True)
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
    # For numeric sizes (shoes, etc.)
    numeric_size = models.PositiveIntegerField(blank=True, null=True)
    # For alphabetic sizes (clothes, etc.)
    alpha_size = models.CharField(max_length=10, blank=True, null=True, 
                                  help_text="e.g., XS, S, M, L, XL, XXL")
    # For any custom size description
    custom_size = models.CharField(max_length=50, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'
        ordering = ['size_type', 'numeric_size', 'alpha_size']
        # Ensure uniqueness based on size type and value
        unique_together = [
            ['size_type', 'numeric_size'],
            ['size_type', 'alpha_size'],
            ['size_type', 'custom_size']
        ]
    
    def clean(self):
        # Ensure only one size field is filled based on size_type
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
        srid=4326,  # Standard SRID for latitude/longitude (WGS84)
        blank=True,
        null=True,
        help_text="Geographic location (Point) of the shop (Longitude, Latitude)."
    )
    description = models.TextField(blank=True, null=True)
    # Add business registration fields
    is_active = models.BooleanField(default=True, help_text="Whether the shop is currently active")
    is_verified = models.BooleanField(default=False, help_text="Whether the shop is verified by admin")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Shop'
        verbose_name_plural = 'Shops'
        ordering = ['-created_at']
        # Ensure one user can only have one shop (optional - remove if users can have multiple shops)
        # unique_together = ['owner']
    
    def __str__(self):
        return f"{self.name} (Owner: {self.owner.username})"
    
    @property
    def latitude(self):
        return self.location.y if self.location else None
    
    @property
    def longitude(self):
        return self.location.x if self.location else None

class Product(models.Model):
    """
    Base Product model - represents the general product (e.g., "Summer Dress")
    Specific variants with size/color/price are handled by ProductVariant model
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=False, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=False, related_name='products')
    description = models.TextField(blank=True, null=True, help_text="Detailed product description")
    
    # Available sizes and colors for this product (many-to-many relationships)
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
    
    def get_compatible_sizes(self):
        """Get sizes that are compatible with this product's category"""
        if self.category:
            return Size.objects.filter(size_type=self.category.size_type)
        return Size.objects.none()
    
    def get_variant(self, size, color):
        """Get specific variant for given size and color"""
        try:
            return self.variants.get(size=size, color=color)
        except ProductVariant.DoesNotExist:
            return None
    
    def get_min_price(self):
        """Get minimum price among all variants"""
        prices = self.variants.values_list('price', flat=True)
        return min(prices) if prices else None
    
    def get_max_price(self):
        """Get maximum price among all variants"""
        prices = self.variants.values_list('price', flat=True)
        return max(prices) if prices else None
    
    def get_total_stock(self):
        """Get total stock across all variants"""
        return sum(self.variants.values_list('quantity', flat=True))

class ProductVariant(models.Model):
    """
    Product Variant model - represents specific combinations of Product + Size + Color
    Each variant has its own price and inventory
    This replaces your ProductSize and ProductColor models
    """
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='product_variants')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='product_variants')
    
    # Pricing and inventory for this specific variant
    price = models.DecimalField(max_digits=10, decimal_places=2,
                               help_text="Price for this specific size/color combination")
    quantity = models.PositiveIntegerField(default=0,
                                         help_text="Available quantity for this variant")
    
    # Optional: SKU for this specific variant
    sku = models.CharField(max_length=100, blank=True, null=True, unique=True,
                          help_text="Stock Keeping Unit - unique identifier for this variant")
    
    # Optional: Additional description for this variant
    description = models.TextField(blank=True, null=True,
                                 help_text="Additional notes for this specific variant")
    
    is_active = models.BooleanField(default=True, help_text="Whether this variant is available")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'
        # Ensure each product can have each size/color combination only once
        unique_together = ['product', 'size', 'color']
        ordering = ['product__name', 'size__size_type', 'size__numeric_size', 'size__alpha_size', 'color__color_name']
    
    def clean(self):
        # Validate that the size type matches the product's category size type
        if self.product and self.product.category and self.size:
            if self.size.size_type != self.product.category.size_type:
                raise ValidationError(
                    f"Size type '{self.size.size_type}' doesn't match category '{self.product.category.category_name}' "
                    f"which requires '{self.product.category.size_type}' sizes."
                )
        
        # Validate that the size and color are in the product's available options
        if self.product and self.size:
            if not self.product.available_sizes.filter(id=self.size.id).exists():
                raise ValidationError(f"Size '{self.size}' is not available for product '{self.product.name}'.")
        
        if self.product and self.color:
            if not self.product.available_colors.filter(id=self.color.id).exists():
                raise ValidationError(f"Color '{self.color}' is not available for product '{self.product.name}'.")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} - {self.size}, {self.color} (${self.price}, Qty: {self.quantity})"

class ProductImage(models.Model):
    """Updated to work with ProductVariant instead of separate ProductColor"""
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    # Optional: Associate images with specific variants
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True, related_name='images',
                               help_text="Associate image with a specific product variant")
    # Keep color field for backward compatibility or for images that apply to all sizes of a color
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name='images',
                             help_text="Associate image with a specific color (applies to all sizes)")
    
    front_image = models.ImageField(upload_to='product/images/front_images/', blank=True, null=True)
    back_image = models.ImageField(upload_to='product/images/back_images/', blank=True, null=True)
    side_image = models.ImageField(upload_to='product/images/side_images/', blank=True, null=True)
    aerial_image = models.ImageField(upload_to='product/images/aerial_images/', blank=True, null=True)
    is_primary = models.BooleanField(default=False,
                                   help_text="Primary image for this product/variant/color combination")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'
        ordering = ['product__name', 'color__color_name', '-is_primary']
    
    def __str__(self):
        if self.variant:
            return f"Images for {self.variant} [PRIMARY]" if self.is_primary else f"Images for {self.variant}"
        elif self.color:
            return f"Images for {self.product.name} ({self.color.color_name}) [PRIMARY]" if self.is_primary else f"Images for {self.product.name} ({self.color.color_name})"
        else:
            return f"Images for {self.product.name} [PRIMARY]" if self.is_primary else f"Images for {self.product.name}"

class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]  # 1 to 5 stars
    
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    # Optional: Review specific variant
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True, related_name='reviews',
                               help_text="Review for specific variant (size/color combination)")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ['product', 'user']  # One review per user per product
        ordering = ['-created_at']
    
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
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    # Instead of separate product, size, color - use variant
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,
                                   help_text="Price per unit at time of order")
    total_price = models.DecimalField(max_digits=10, decimal_places=2,
                                    help_text="Total price for this order line")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    
    # Delivery-related fields
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
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Auto-calculate total price
        if self.unit_price and self.quantity:
            self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)
    
    # Properties for backward compatibility
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
    # Instead of separate product, size, color - use variant
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['user', 'variant']  # Prevent duplicate cart items for same variant
        ordering = ['-added_at']
    
    def get_total_price(self):
        """Calculate total price for this cart item"""
        return self.variant.price * self.quantity
    
    # Properties for backward compatibility
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
        unique_together = ['user', 'product']  # Prevent duplicate wishlist items
        ordering = ['-added_at']
    
    def __str__(self):
        return f"WishlistItem: {self.product.name} for {self.user.username}"

# Optional: Create a dedicated Delivery model for better delivery tracking
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
    
    def __str__(self):
        return f"Delivery #{self.id} - Order #{self.order.id} by {self.deliverer.username}"