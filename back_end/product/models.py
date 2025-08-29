from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

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

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=False, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=False, related_name='products')
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

# Intermediate model for Product-Size relationship with pricing and inventory
class ProductSize(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_sizes')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='product_sizes')
    price = models.DecimalField(max_digits=10, decimal_places=2, 
                               help_text="Price for this specific size of the product")
    quantity = models.PositiveIntegerField(default=0, 
                                         help_text="Available quantity for this size")
    description = models.TextField(blank=True, null=True,
                                 help_text="Additional notes for this size variant")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Size'
        verbose_name_plural = 'Product Sizes'
        unique_together = ['product', 'size']  # A product can have each size only once
        ordering = ['product__name', 'size__size_type', 'size__numeric_size', 'size__alpha_size']
    
    def clean(self):
        # Validate that the size type matches the product's category size type
        if self.product and self.product.category and self.size:
            if self.size.size_type != self.product.category.size_type:
                raise ValidationError(
                    f"Size type '{self.size.size_type}' doesn't match category '{self.product.category.category_name}' "
                    f"which requires '{self.product.category.size_type}' sizes."
                )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.product.name} - {self.size} (${self.price}, Qty: {self.quantity})"

# Intermediate model for Product-Color relationship with color-specific pricing
class ProductColor(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_colors')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='product_colors')
    price_modifier = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                       help_text="Additional cost for this color (can be negative for discounts)")
    is_available = models.BooleanField(default=True, 
                                     help_text="Whether this color is currently available")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product Color'
        verbose_name_plural = 'Product Colors'
        unique_together = ['product', 'color']  # A product can have each color only once
        ordering = ['product__name', 'color__color_name']
    
    def __str__(self):
        modifier_str = f" (+${self.price_modifier})" if self.price_modifier > 0 else f" (${self.price_modifier})" if self.price_modifier < 0 else ""
        return f"{self.product.name} - {self.color.color_name}{modifier_str}"

class ProductImage(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name='images',
                             help_text="Associate image with a specific color variant")
    front_image = models.ImageField(upload_to='product/images/front_images/', blank=True, null=True)
    back_image = models.ImageField(upload_to='product/images/back_images/', blank=True, null=True)
    side_image = models.ImageField(upload_to='product/images/side_images/', blank=True, null=True)
    aerial_image = models.ImageField(upload_to='product/images/aerial_images/', blank=True, null=True)
    is_primary = models.BooleanField(default=False,
                                   help_text="Primary image for this product/color combination")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Image'
        verbose_name_plural = 'Images'
        ordering = ['product__name', 'color__color_name', '-is_primary']
    
    def __str__(self):
        color_info = f" ({self.color.color_name})" if self.color else ""
        primary_info = " [PRIMARY]" if self.is_primary else ""
        return f"Images for {self.product.name}{color_info}{primary_info}"

class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]  # 1 to 5 stars
    
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
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
        return f"Review by {self.user.username} for {self.product.name} ({self.rating}★)"

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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='orders')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2,
                                   help_text="Price per unit at time of order")
    total_price = models.DecimalField(max_digits=10, decimal_places=2,
                                    help_text="Total price for this order line")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
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
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username} for {self.product.name} ({self.size}, {self.color.color_name})"

class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='cart_items')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        unique_together = ['user', 'product', 'size', 'color']  # Prevent duplicate cart items
        ordering = ['-added_at']
    
    def get_total_price(self):
        """Calculate total price for this cart item including size and color modifiers"""
        try:
            product_size = ProductSize.objects.get(product=self.product, size=self.size)
            product_color = ProductColor.objects.get(product=self.product, color=self.color)
            base_price = product_size.price
            color_modifier = product_color.price_modifier
            return (base_price + color_modifier) * self.quantity
        except (ProductSize.DoesNotExist, ProductColor.DoesNotExist):
            return 0
    
    def __str__(self):
        return f"CartItem: {self.quantity} of {self.product.name} ({self.size}, {self.color.color_name}) for {self.user.username}"

class WishlistItem(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        unique_together = ['user', 'product']  # Prevent duplicate wishlist items
        ordering = ['-added_at']
    
    def __str__(self):
        return f"WishlistItem: {self.product.name} for {self.user.username}"