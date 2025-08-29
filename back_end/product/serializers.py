from product.models import Product, Size, Color, Category, Brand, Review, Order, CartItem, WishlistItem,ProductSize, ProductColor,ProductImage
from rest_framework import serializers
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all_'
        
        def validate_name(self, value):
            if not value:
                raise serializers.ValidationError("Product name cannot be empty.")
            return value
        
        # def validate_sizes(self, value):
        #     if not value:
        #         raise serializers.ValidationError("Product must have at least one size.")
        #     return value
        
        # def validate_colors(self, value):
        #     if not value:
        #         raise serializers.ValidationError("Product must have at least one color.")
        #     return value
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
        fields = '__all_'
    # def validate_price(self, value):
    #     if value < 0:
    #         raise serializers.ValidationError("Price must be a positive number.")
    #     return value

    # def validate_quantity(self, value):
    #     if value < 0:
    #         raise serializers.ValidationError("Stock must be a non-negative integer.")
    #     return value
class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all_'
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSize
        fields = '__all_'
        read_only_fields = ['id', 'created_at', 'updated_at']
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock must be a non-negative integer.")
        return value
class ProductColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductColor
        fields = '__all_'
        read_only_fields = ['id', 'created_at', 'updated_at']
    def validate_price_modifier(self, value):
        if value < 0:
            raise serializers.ValidationError("Price modifier must be a positive number.")
        return value
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all_'
        read_only_fields = ['id', 'created_at', 'updated_at']
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all_'
        read_only_fields = ['id', 'created_at', 'updated_at']
class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all_'
        read_only_fields = ['id', 'created_at', 'updated_at']
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all_'
        read_only_fields = ['id', 'created_at', 'updated_at']
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all_'
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
        fields = '__all_'
        read_only_fields = ['id', 'added_at']
        
        def validate_quantity(self, value):
            if value < 0:
                raise serializers.ValidationError("Quantity of items in the cart must be a postive number")
            return value
class WishlistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistItem
        fields = '__all_'
        read_only_fields = ['id', 'added_at']
        