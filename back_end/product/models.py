from django.db import models
class Product(models.Model):
    id= models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    brand = models.ForeignKey('Brand', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    sizes = models.ManyToManyField('Size', blank=True, related_name='products')
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    colors = models.ManyToManyField('Color', blank=True, related_name='products')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']
    def __str__(self):
        return str(self.name) if self.name is not None else "Unnamed Product"

class Size(models.Model):
    id= models.AutoField(primary_key=True)
    productName = models.CharField(max_length=50)
    size = models.PositiveIntegerField(blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='sizes')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'
        ordering = ['size','productName','price']
    def __str__(self):
        return str(self.size) if self.productName is not None else "Unnamed Size"
class Color(models.Model):
    id= models.AutoField(primary_key=True)
    productName = models.CharField(max_length=50)
    hex_code = models.CharField(max_length=7, blank=True, null=True)  # e.g., #FFFFFF
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Color'
        verbose_name_plural = 'Colors'
        ordering = ['productName']
    def __str__(self):
        return str(self.hex_code) if self.productName is not None else "Unnamed Color"

class Category(models.Model):
    id= models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
    def __str__(self):
        return str(self.name) if self.name is not None else "Unnamed Category"

class Brand(models.Model):
    id= models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='brand_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']
    def __str__(self):
        return str(self.name) if self.name is not None else "Unnamed Brand"
class Review(models.Model):
    id= models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('User.User', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
    def __str__(self):
        return f"Review by {self.user} for {self.product}" if self.user is not None and self.product is not None else "Unnamed Review"
class Order(models.Model):
    id= models.AutoField(primary_key=True)
    user = models.ForeignKey('User.User', on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']
    def __str__(self):
        return f"Order by {self.user} for {self.product}" if self.user is not None and self.product is not None else "Unnamed Order"
class CartItem(models.Model):
    id= models.AutoField(primary_key=True)
    user = models.ForeignKey('User.User', on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        ordering = ['-added_at']
    def __str__(self):
        return f"CartItem: {self.quantity} of {self.product} for {self.user}" if self.user is not None and self.product is not None else "Unnamed CartItem"
class WishlistItem(models.Model):
    id= models.AutoField(primary_key=True)
    user = models.ForeignKey('User.User', on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        ordering = ['-added_at']
    def __str__(self):
        return f"WishlistItem: {self.product} for {self.user}" if self.user is not None and self.product is not None else "Unnamed WishlistItem"

