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
    list_display = ('name', 'category', 'brand__brandName', 'created_at')
    list_filter = ('brand', 'category', 'created_at')
    search_fields = ('name', 'category__categoryName', 'brand__brandName')
    list_editable = []
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('brandName', 'created_at')
    search_fields = ('brandName', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('categoryName', 'created_at')
    search_fields = ('categoryName', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('size','price','quantity','description','created_at')
    list_filter = ('size','price','created_at')
    search_fields = ('price','size')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('product', 'hex_code','colorName','created_at')
    search_fields = ('product__name','hex_code','colorName')
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