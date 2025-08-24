from django.contrib import admin
from .models import Product, Size, Color, Category, Brand, Review, Order, CartItem, WishlistItem

admin.site.site_header = "Mutovu Market Administration"
admin.site.site_title = "Mutovu Market Admin Portal"
admin.site.index_title = "Welcome to Mutovu Market Administration"


# admin.site.register(Product)
# admin.site.register(Size)
# admin.site.register(Color)
# admin.site.register(Category)
# admin.site.register(Brand)
# admin.site.register(Review)
# admin.site.register(Order)
# admin.site.register(CartItem)
# admin.site.register(WishlistItem)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category','image', 'created_at')
    list_filter = ('brand', 'category', 'sizes','colors', 'created_at')
    search_fields = ('name', 'description', 'category__name', 'brand__name')
    filter_horizontal = ('sizes', 'colors')
    list_editable = []
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('productName', 'size', 'price', 'category', 'quantity')
    list_filter = ('category',)
    search_fields = ('productName',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('productName', 'hex_code', 'created_at')
    search_fields = ('productName',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'product__name')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')