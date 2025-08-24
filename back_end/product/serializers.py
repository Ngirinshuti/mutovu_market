from product.models import Product, Size, Color, Category, Brand, Review, Order, CartItem, WishlistItem
from rest_framework import serializers
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'brand', 'sizes', 'colors', 'category', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
        def validate_name(self, value):
            if not value:
                raise serializers.ValidationError("Product name cannot be empty.")
            return value
        
        def validate_sizes(self, value):
            if not value:
                raise serializers.ValidationError("Product must have at least one size.")
            return value
        
        def validate_colors(self, value):
            if not value:
                raise serializers.ValidationError("Product must have at least one color.")
            return value
        def validate_category(self, value):
            if not value:
                raise serializers.ValidationError("Product must belong to a category.")
            return value
        
        def validate_image(self, value):
            if not value:
                raise serializers.ValidationError("Product image cannot be empty.")
            return value

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'productName', 'size', 'category', 'price', 'quantity', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock must be a non-negative integer.")
        return value
class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'productName', 'hex_code', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'name', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'user', 'product', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'product', 'quantity', 'total_price', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def validate_total_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Total Price must be a positive number.")
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity of ordered items must be a non-negative integer.")
        return value
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'user', 'product', 'quantity', 'added_at']
        read_only_fields = ['id', 'added_at']
        
        def validate_quantity(self, value):
            if value < 0:
                raise serializers.ValidationError("Quantity of items in the cart must be a postive number")
            return value
class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = ['id', 'user', 'product', 'added_at']
        read_only_fields = ['id', 'added_at']
        