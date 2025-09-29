from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet, SizeViewSet, ColorViewSet, CategoryViewSet,
    BrandViewSet, ReviewViewSet, OrderViewSet, CartItemViewSet,
    WishlistItemViewSet, ShopViewSet, ProductVariantViewSet,
    ProductImageViewSet, DeliveryViewSet
)

router = DefaultRouter(trailing_slash=False)

# Main product-related endpoints
router.register(r'products', ProductViewSet, basename='product')
router.register(r'sizes', SizeViewSet, basename='size')
router.register(r'colors', ColorViewSet, basename='color')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')

# NEW: Product variants (replaces product-sizes and product-colors)
router.register(r'product-variants', ProductVariantViewSet, basename='productvariant')

# Product images
router.register(r'product-images', ProductImageViewSet, basename='productimage')

# Shop management
router.register(r'shops', ShopViewSet, basename='shop')

# Order and transaction management
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'cart-items', CartItemViewSet, basename='cartitem')
router.register(r'wishlist-items', WishlistItemViewSet, basename='wishlistitem')

# Reviews
router.register(r'reviews', ReviewViewSet, basename='review')

# Deliverer-specific endpoints
router.register(r'deliveries', DeliveryViewSet, basename='deliverer')

urlpatterns = [
    path('', include(router.urls)),
]