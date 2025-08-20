from django.db import models
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from django.db.models.manager import Manager
class Product(models.Model):
    id= models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    category = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']
    def __str__(self):
        return str(self.name) if self.name is not None else "Unnamed Product"
if TYPE_CHECKING:
    objects: Manager['Product']
