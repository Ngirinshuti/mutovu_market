from product.models import (
    Product, Shop, Size, Color, Category, Brand, Review, Order, 
    CartItem, WishlistItem, ProductVariant, ProductImage, Delivery
)
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometryField


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariant model"""
    size_details = SizeSerializer(source='size', read_only=True)
    color_details = ColorSerializer(source='color', read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity must be a non-negative integer.")
        return value

    def validate(self, data):
        """Validate that the variant combination doesn't already exist for this product"""
        product = data.get('product')
        size = data.get('size')
        color = data.get('color')
        
        if product and size and color:
            # Check for existing variant with same product, size, color (excluding current instance during update)
            existing_variant = ProductVariant.objects.filter(
                product=product, size=size, color=color
            )
            if self.instance:
                existing_variant = existing_variant.exclude(id=self.instance.id)
            
            if existing_variant.exists():
                raise serializers.ValidationError(
                    "A variant with this size and color combination already exists for this product."
                )
        
        return data


class ProductImageSerializer(serializers.ModelSerializer):
    color_details = ColorSerializer(source='color', read_only=True)
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    
    class Meta:
        model = ProductImage
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShopSerializer(GeoFeatureModelSerializer):
    location = GeometryField()
    # Add computed fields for easier access
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = Shop
        fields = (
            'id', 'name', 'phone', 'email', 'address', 'description', 
            'location', 'latitude', 'longitude', 'created_at'
        )
        read_only_fields = ['id', 'created_at', 'latitude', 'longitude']
        geo_field = "location"
    
    def get_latitude(self, obj):
        return obj.latitude
    
    def get_longitude(self, obj):
        return obj.longitude


class ProductSerializer(serializers.ModelSerializer):
    # Nested serializers for related objects
    brand_details = BrandSerializer(source='brand', read_only=True)
    category_details = CategorySerializer(source='category', read_only=True)
    shop_details = ShopSerializer(source='shop', read_only=True)
    
    # Related data - Updated to use ProductVariant
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    # Size and color details for available options
    available_sizes_details = SizeSerializer(source='available_sizes', many=True, read_only=True)
    available_colors_details = ColorSerializer(source='available_colors', many=True, read_only=True)
    
    # Computed fields
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    variant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at']
        
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Product name cannot be empty.")
        return value
        
    def validate_category(self, value):
        if not value:
            raise serializers.ValidationError("Product must belong to a category.")
        return value
    
    def get_avg_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return round(sum(review.rating for review in reviews) / len(reviews), 1)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.count()
    
    def get_min_price(self, obj):
        return obj.get_min_price()
    
    def get_max_price(self, obj):
        return obj.get_max_price()
    
    def get_total_stock(self, obj):
        return obj.get_total_stock()
    
    def get_variant_count(self, obj):
        return obj.variants.count()


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    
    class Meta:
        model = Review
        fields = "__all__"
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
        
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


# Add this to your serializers.py file

class OrderSerializer(serializers.ModelSerializer):
    """Enhanced Order serializer with all needed data for frontend"""
    
    # User details
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_details = serializers.SerializerMethodField()
    
    # Variant details with nested product, size, color info
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    
    # Direct access fields for easier frontend usage
    customer_name = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    product_id = serializers.IntegerField(source='variant.product.id', read_only=True)
    size_name = serializers.SerializerMethodField()
    color_name = serializers.CharField(source='variant.color.color_name', read_only=True)
    shop_id = serializers.IntegerField(source='variant.product.shop.id', read_only=True)
    shop_name = serializers.CharField(source='variant.product.shop.name', read_only=True)
    
    # Backward compatibility fields (your frontend expects these)
    product = serializers.IntegerField(source='variant.product.id', read_only=True)
    size = serializers.IntegerField(source='variant.size.id', read_only=True)
    color = serializers.IntegerField(source='variant.color.id', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'variant', 'quantity', 'unit_price', 'total_price',
            'status', 'delivery_address', 'delivery_fee', 'estimated_delivery_time',
            'deliverer', 'created_at', 'updated_at',
            # Additional fields for frontend
            'user_name', 'user_details', 'variant_details',
            'customer_name', 'product_name', 'product_id', 'size_name', 'color_name',
            'shop_id', 'shop_name',
            # Backward compatibility
            'product', 'size', 'color'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_user_details(self, obj):
        """Get user details"""
        user = obj.user
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    
    def get_customer_name(self, obj):
        """Get customer display name"""
        user = obj.user
        if user.first_name and user.last_name:
            return f"{user.first_name} {user.last_name}"
        return user.username
    
    def get_size_name(self, obj):
        """Get size display name"""
        size = obj.variant.size
        if size.size_type == 'numeric' and size.numeric_size:
            return str(size.numeric_size)
        elif size.size_type == 'alpha' and size.alpha_size:
            return size.alpha_size
        elif size.size_type == 'custom' and size.custom_size:
            return size.custom_size
        return f"Size {size.id}"


class CartItemSerializer(serializers.ModelSerializer):
    variant_details = ProductVariantSerializer(source='variant', read_only=True)
    total_price = serializers.SerializerMethodField()
    
    # Backward compatibility
    product = serializers.CharField(source='variant.product.id', read_only=True)
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    size = serializers.CharField(source='variant.size.id', read_only=True)
    color = serializers.CharField(source='variant.color.id', read_only=True)
    size_details = serializers.SerializerMethodField()
    color_details = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = "__all__"
        read_only_fields = ['id', 'added_at', 'user']
        
    def get_size_details(self, obj):
        if obj.variant and obj.variant.size:
            return SizeSerializer(obj.variant.size).data
        return None
    
    def get_color_details(self, obj):
        if obj.variant and obj.variant.color:
            return ColorSerializer(obj.variant.color).data
        return None
        
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive number.")
        return value
    
    def get_total_price(self, obj):
        return obj.get_total_price()

    def validate(self, data):
        """Validate that the variant has sufficient stock"""
        if 'variant' in data and 'quantity' in data:
            variant = data['variant']
            quantity = data['quantity']
            
            if variant.quantity < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock. Only {variant.quantity} items available."
                )
        
        return data


class WishlistItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_details = ProductSerializer(source='product', read_only=True)
    
    class Meta:
        model = WishlistItem
        fields = "__all__"
        read_only_fields = ['id', 'added_at', 'user']


# Simplified serializers for creation/updates
class ProductCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating products."""
    
    class Meta:
        model = Product
        fields = ['name', 'shop', 'brand', 'category', 'description', 'available_sizes', 'available_colors', 'is_active']
        
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Product name cannot be empty.")
        return value

    def validate_available_sizes(self, value):
        """Validate that sizes match the category's size type"""
        if hasattr(self, 'initial_data') and 'category' in self.initial_data:
            try:
                from .models import Category, Size
                category = Category.objects.get(id=self.initial_data['category'])
                invalid_sizes = Size.objects.filter(
                    id__in=[size.id if hasattr(size, 'id') else size for size in value]
                ).exclude(size_type=category.size_type)
                
                if invalid_sizes.exists():
                    invalid_names = [str(size) for size in invalid_sizes]
                    raise serializers.ValidationError(
                        f"These sizes don't match the category size type ({category.size_type}): {', '.join(invalid_names)}"
                    )
            except Category.DoesNotExist:
                pass
        
        return value


class ProductVariantCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating product variants."""
    
    class Meta:
        model = ProductVariant
        fields = ['product', 'size', 'color', 'price', 'quantity', 'sku', 'description', 'is_active']
        
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value


class ShopCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating shops."""
    location = GeometryField()
    
    class Meta:
        model = Shop
        fields = ['name', 'phone', 'email', 'address', 'description', 'location']
        
    def validate_name(self, value):
        if not value:
            raise serializers.ValidationError("Shop name cannot be empty.")
        return value
    
    def validate_phone(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required.")
        return value
    
    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        return value


# Bulk operation serializers
class BulkVariantCreateSerializer(serializers.Serializer):
    """Serializer for creating multiple variants at once"""
    product = serializers.IntegerField()
    variants = ProductVariantCreateSerializer(many=True)
    
    def validate_product(self, value):
        try:
            from .models import Product
            product = Product.objects.get(id=value)
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product does not exist.")
    
    def create(self, validated_data):
        """Create multiple variants for a product"""
        product_id = validated_data['product']
        variants_data = validated_data['variants']
        
        created_variants = []
        for variant_data in variants_data:
            variant_data['product'] = product_id
            serializer = ProductVariantCreateSerializer(data=variant_data)
            if serializer.is_valid():
                created_variants.append(serializer.save())
            else:
                # If any variant fails, you might want to handle this differently
                raise serializers.ValidationError(serializer.errors)
        
        return created_variants


class BulkPriceUpdateSerializer(serializers.Serializer):
    """Serializer for bulk price updates"""
    updates = serializers.ListField(
        child=serializers.DictField(
            child=serializers.DecimalField(max_digits=10, decimal_places=2)
        )
    )
    
    def validate_updates(self, value):
        """Validate that all updates have required fields"""
        for update in value:
            if 'id' not in update or 'price' not in update:
                raise serializers.ValidationError("Each update must have 'id' and 'price' fields.")
            if update['price'] <= 0:
                raise serializers.ValidationError("Price must be greater than zero.")
        return value


# Statistics and reporting serializers
class VariantStatsSerializer(serializers.Serializer):
    """Serializer for variant statistics"""
    
    total_variants = serializers.IntegerField()
    active_variants = serializers.IntegerField()
    inactive_variants = serializers.IntegerField()
    out_of_stock = serializers.IntegerField()
    low_stock = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_range = serializers.DictField()


class ProductStatsSerializer(serializers.Serializer):
    """Serializer for product statistics"""
    
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    products_with_variants = serializers.IntegerField()
    products_without_variants = serializers.IntegerField()
    variant_stats = VariantStatsSerializer()


# Search and filter serializers
class VariantSearchSerializer(serializers.Serializer):
    """Serializer for variant search parameters"""
    
    search = serializers.CharField(required=False, allow_blank=True)
    shop = serializers.IntegerField(required=False)
    category = serializers.IntegerField(required=False)
    brand = serializers.IntegerField(required=False)
    size = serializers.IntegerField(required=False)
    color = serializers.IntegerField(required=False)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    in_stock = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    ordering = serializers.ChoiceField(
        choices=[
            'price', '-price', 'quantity', '-quantity', 
            'created_at', '-created_at', 'product__name'
        ],
        required=False
    )
    
class DeliverySerializer(serializers.ModelSerializer):
    order_details = OrderSerializer(source='order', read_only=True)
    
    class Meta:
        model = Delivery
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']