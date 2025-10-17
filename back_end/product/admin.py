from django.contrib import admin
from .models import Product, Size, Color, Category, Brand, Review, Order, CartItem, WishlistItem,ProductImage,Shop,ProductVariant,Delivery,SubCategory

admin.site.site_header = "Mutovu Market Administration"
admin.site.site_title = "Mutovu Market Admin Portal"
admin.site.index_title = "Welcome to Mutovu Market Administration"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # Corrected 'category__categoryName' to 'category__category_name'
    # Corrected 'brand' to 'brand__brand_name' in search_fields
    list_display = ('name', 'category', 'brand', 'created_at')
    list_filter = ('brand', 'category', 'created_at')
    search_fields = ('name', 'category', 'brand')
    list_editable = []
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'quantity', 'price', 'created_at')
    list_filter = ('product', 'size', 'color', 'created_at')
    search_fields = ('product__name', 'size__custom_size', 'color__color_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('brand_name', 'created_at')
    search_fields = ('brand_name', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name','size_type', 'created_at')
    search_fields = ('category_name','size_type', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('subcategory_name','category', 'description', 'created_at')
    search_fields = ('subcategory_name','category')
    readonly_fields = ('created_at', 'updated_at')
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('size_type','numeric_size','alpha_size','custom_size','created_at')
    list_filter = ('size_type','created_at') # numeric_size, alpha_size, custom_size aren't ideal for list_filter as they are nullable. Filtering on `size_type` is more robust.
    search_fields = ('size_type','numeric_size','alpha_size','custom_size')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('color_name','hex_code','created_at')
    search_fields = ('color_name','hex_code')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating','comment', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity','size','color', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'product__name')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity','size','color', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')
@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'location', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('owner__username', 'name', 'location')
    readonly_fields = ('created_at', 'updated_at')  

# @admin.register(Delivery)
# class DeliveryAdmin(admin.ModelAdmin):
#     list_display = ('order', 'deliverer', 'status', 'assigned_at')
#     list_filter = ('status', 'assigned_at')
#     search_fields = ('order__id', 'deliverer__username')
#     readonly_fields = ('assigned_at', 'updated_at') 