from product.models import (
    Product, Shop, Size, Color, Category, Brand, Review, Order, 
    CartItem, WishlistItem, ProductVariant, ProductImage, Delivery,SubCategory
)
from rest_framework import serializers
from rest_framework_gis.serializers import GeometryField
from django.db.models import Avg, Min, Max, Sum, Count


# ============================================================================
# BASIC SERIALIZERS (For nested/read-only use)
# ============================================================================

class SizeSerializer(serializers.ModelSerializer):
    display = serializers.SerializerMethodField()
    
    class Meta:
        model = Size
        fields = ['id', 'size_type', 'display', 'numeric_size', 'alpha_size', 'custom_size', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_display(self, obj):
        return str(obj)


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'color_name', 'hex_code', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ShopBasicSerializer(serializers.ModelSerializer):
    """Lightweight shop serializer for nested use"""
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = Shop
        fields = ['id', 'name', 'address', 'phone', 'email', 'latitude', 'longitude', 'is_active', 'is_verified']
    
    def get_latitude(self, obj):
        return obj.latitude
    
    def get_longitude(self, obj):
        return obj.longitude

class SubCategorySerializer(serializers.ModelSerializer):
    """Serializer for SubCategory"""
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    
    class Meta:
        model = SubCategory
        fields = ['id', 'category', 'category_name', 'subcategory_name', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
        
class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    subcategory_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'description', 'image', 'size_type', 'subcategories', 'subcategory_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_subcategory_count(self, obj):
        return obj.subcategories.count()

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ['id', 'brand_name', 'description', 'image', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


# ============================================================================
# PRODUCT IMAGE SERIALIZERS
# ============================================================================

class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images with Cloudinary support - FIXED"""
    # front_image = serializers.SerializerMethodField()
    class Meta:
        model = ProductImage
        fields = [
            'id', 'variant', 'front_image', 'back_image', 
            'side_image', 'aerial_image', 'is_primary', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate(self, data):
        """Ensure at least one image is provided"""
        if not any([
            data.get('front_image'),
            data.get('back_image'),
            data.get('side_image'),
            data.get('aerial_image')
        ]):
            raise serializers.ValidationError(
                'At least one image must be provided'
            )
        
        # Ensure variant is provided
        if not data.get('variant'):
            raise serializers.ValidationError(
                'variant field is required'
            )
        
        return data


class ProductImageDetailSerializer(serializers.ModelSerializer):
    """Detailed image serializer with all image URLs"""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'variant', 'front_image', 'back_image', 'side_image', 'aerial_image', 'is_primary', 'created_at']
        read_only_fields = ['id', 'variant', 'created_at']


# ============================================================================
# PRODUCT VARIANT SERIALIZERS
# ============================================================================

class ProductVariantSerializer(serializers.ModelSerializer):
    """Standard variant serializer for list/detail views"""
    size = SizeSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    images = ProductImageDetailSerializer(many=True, read_only=True)
    shop = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'size', 'color', 'price', 'quantity', 'sku', 
            'description', 'is_active', 'images', 'primary_image', 'shop',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_shop(self, obj):
        """Get shop information from the product"""
        if obj.product and obj.product.shop:
            return ShopBasicSerializer(obj.product.shop).data
        return None
    
    def get_primary_image(self, obj):
        """Get the primary image"""
        primary = obj.get_primary_image()
        if primary:
            return ProductImageDetailSerializer(primary).data
        return None


class ProductVariantCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating variants - FIXED to handle null sizes"""
    
    class Meta:
        model = ProductVariant
        fields = ['product', 'size', 'color', 'price', 'quantity', 'sku', 'description', 'is_active']
    
    def validate(self, data):
        """Custom validation to allow null size for certain categories"""
        product = data.get('product')
        size = data.get('size')
        
        # Check if the product's category requires a size
        if product and product.category:
            category_size_type = product.category.size_type
            
            # Size is required for numeric and alpha types
            if category_size_type in ['numeric', 'alpha'] and not size:
                raise serializers.ValidationError({
                    'size': f'Size is required for {category_size_type} category types'
                })
            
            # Size is optional for custom types
            # (null size is allowed)
        
        # Ensure color is always provided
        if not data.get('color'):
            raise serializers.ValidationError({
                'color': 'Color is required for all variants'
            })
        
        return data

class ProductVariantDetailSerializer(serializers.ModelSerializer):
    """Enhanced variant serializer with full nested details"""
    size = SizeSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True) 
    product_details = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'product', 'product_details', 'size', 'color', 'price', 'quantity',
            'sku', 'description', 'is_active', 'images', 'primary_image', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'product', 'created_at', 'updated_at']
    
    def get_product_details(self, obj):
        """Get full product details"""
        return {
            'id': obj.product.id,
            'name': obj.product.name,
            'description': obj.product.description,
            'category': CategorySerializer(obj.product.category).data if obj.product.category else None,
            'brand': BrandSerializer(obj.product.brand).data if obj.product.brand else None,
        }
    
    def get_primary_image(self, obj):
        """Get the primary image"""
        primary = obj.get_primary_image()
        if primary:
            return ProductImageDetailSerializer(primary).data
        return None


# ============================================================================
# PRODUCT SERIALIZERS
# ============================================================================

class ProductSerializer(serializers.ModelSerializer):
    """Standard product serializer"""
    brand = BrandSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    subcategory = SubCategorySerializer(read_only=True)  # NEW
    shop = ShopBasicSerializer(read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    available_sizes = SizeSerializer(many=True, read_only=True)
    available_colors = ColorSerializer(many=True, read_only=True)
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    variant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'brand', 'category', 'subcategory', 'shop',  # Added subcategory
            'variants', 'available_sizes', 'available_colors', 'is_active',
            'avg_rating', 'review_count', 'min_price', 'max_price',
            'total_stock', 'variant_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_avg_rating(self, obj):
        avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(float(avg), 1) if avg else 0.0
    
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


class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating products"""
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'brand', 'category', 'subcategory', 'shop', 'is_active', 'created_at', 'updated_at']  # Added subcategory
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'shop': {'required': True},
            'category': {'required': True},
            'brand': {'required': True},
            'subcategory': {'required': False},  # Optional
        }
    
    def validate(self, data):
        """Validate that subcategory belongs to category if provided"""
        category = data.get('category')
        subcategory = data.get('subcategory')
        
        if subcategory and category:
            if subcategory.category_id != category.id:
                raise serializers.ValidationError({
                    'subcategory': f'Subcategory must belong to the selected category: {category.category_name}'
                })
        
        return data


class ProductListSerializer(serializers.ModelSerializer):
    """Enhanced product serializer for catalog/list views"""
    shop = ShopBasicSerializer(read_only=True)
    category = serializers.SerializerMethodField()
    subcategory = serializers.SerializerMethodField()  # NEW
    brand = serializers.SerializerMethodField()
    avg_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    total_stock = serializers.SerializerMethodField()
    variant_count = serializers.SerializerMethodField()
    variants = ProductVariantDetailSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'subcategory', 'brand', 'shop',  # Added subcategory
            'variants', 'avg_rating', 'review_count', 'min_price', 'max_price',
            'total_stock', 'variant_count', 'is_active', 'created_at'
        ]
    
    def get_category(self, obj):
        if obj.category:
            return {'id': obj.category.id, 'name': obj.category.category_name}
        return None
    
    def get_subcategory(self, obj):
        """NEW: Return subcategory info"""
        if obj.subcategory:
            return {
                'id': obj.subcategory.id, 
                'name': obj.subcategory.subcategory_name,
                'category_id': obj.subcategory.category_id
            }
        return None
    
    def get_brand(self, obj):
        if obj.brand:
            return {'id': obj.brand.id, 'name': obj.brand.brand_name}
        return None
    
    def get_avg_rating(self, obj):
        avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
        return round(float(avg), 1) if avg else 0.0
    
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

# ============================================================================
# REVIEW SERIALIZERS
# ============================================================================

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for product reviews"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    variant_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'product', 'variant', 'user', 'user_name', 'product_name', 'variant_details', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
    
    def get_variant_details(self, obj):
        if obj.variant:
            return {
                'id': obj.variant.id,
                'size': str(obj.variant.size) if obj.variant.size else None,
                'color': obj.variant.color.color_name if obj.variant.color else None,
            }
        return None
    
    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


# ============================================================================
# CART SERIALIZERS
# ============================================================================

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items with full variant details"""
    variant_details = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    total_price = serializers.SerializerMethodField()
    size_details = serializers.SerializerMethodField()
    color_details = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'variant', 'quantity', 'added_at', 'user',
            'variant_details', 'total_price', 'product_name',
            'size_details', 'color_details'
        ]
        read_only_fields = ['id', 'added_at', 'user']
    
    def get_variant_details(self, obj):
        """Return complete variant information"""
        variant = obj.variant
        primary_image = variant.get_primary_image()
        
        return {
            'id': variant.id,
            'price': float(variant.price),
            'quantity': variant.quantity,
            'sku': variant.sku,
            'product': {
                'id': variant.product.id,
                'name': variant.product.name,
            },
            'primary_image': ProductImageDetailSerializer(primary_image).data if primary_image else None,
            'shop': ShopBasicSerializer(variant.product.shop).data if variant.product.shop else None,
        }
    
    def get_size_details(self, obj):
        if obj.variant and obj.variant.size:
            return {
                'id': obj.variant.size.id,
                'display': str(obj.variant.size),
                'size_type': obj.variant.size.size_type,
            }
        return None
    
    def get_color_details(self, obj):
        if obj.variant and obj.variant.color:
            return {
                'id': obj.variant.color.id,
                'name': obj.variant.color.color_name,
                'hex_code': obj.variant.color.hex_code,
            }
        return None
    
    def get_total_price(self, obj):
        """Get total price for this cart item"""
        return float(obj.get_total_price())
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive number.")
        return value
    
    def validate(self, data):
        """Validate stock availability"""
        if 'variant' in data and 'quantity' in data:
            variant = data['variant']
            quantity = data['quantity']
            
            if variant.quantity < quantity:
                raise serializers.ValidationError({
                    'quantity': f'Insufficient stock. Only {variant.quantity} items available.'
                })
        return data
    
    def create(self, validated_data):
        """Handle duplicate cart items by merging quantities"""
        user = self.context['request'].user
        variant = validated_data['variant']
        quantity = validated_data['quantity']
        
        existing_item = CartItem.objects.filter(user=user, variant=variant).first()
        
        if existing_item:
            new_quantity = existing_item.quantity + quantity
            if variant.quantity < new_quantity:
                raise serializers.ValidationError({
                    'quantity': f'Cannot add {quantity} more items. Only {variant.quantity - existing_item.quantity} available.'
                })
            existing_item.quantity = new_quantity
            existing_item.save()
            return existing_item
        
        return CartItem.objects.create(user=user, variant=variant, quantity=quantity)


# ============================================================================
# WISHLIST SERIALIZERS
# ============================================================================

class WishlistItemSerializer(serializers.ModelSerializer):
    """Serializer for wishlist items"""
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_details = serializers.SerializerMethodField()
    
    class Meta:
        model = WishlistItem
        fields = ['id', 'product', 'product_name', 'product_details', 'added_at', 'user']
        read_only_fields = ['id', 'added_at', 'user']
    
    def get_product_details(self, obj):
        """Return complete product information"""
        product = obj.product
        variants = product.variants.filter(is_active=True)
        prices = [v.price for v in variants]
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        total_stock = sum(v.quantity for v in variants)
        
        # Get primary image from first variant
        primary_image = None
        if variants.exists():
            first_variant = variants.first()
            primary = first_variant.get_primary_image()
            if primary:
                primary_image = ProductImageDetailSerializer(primary).data
        
        reviews = product.reviews.all()
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        
        return {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'min_price': float(min_price),
            'max_price': float(max_price),
            'total_stock': total_stock,
            'avg_rating': round(float(avg_rating), 1) if avg_rating else 0.0,
            'review_count': reviews.count(),
            'primary_image': primary_image,
            'category': CategorySerializer(product.category).data if product.category else None,
            'brand': BrandSerializer(product.brand).data if product.brand else None,
            'is_active': product.is_active,
        }


# ============================================================================
# ORDER SERIALIZERS
# ============================================================================

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders with full details"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_details = serializers.SerializerMethodField()
    variant_details = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    product_name = serializers.CharField(source='variant.product.name', read_only=True)
    product_id = serializers.IntegerField(source='variant.product.id', read_only=True)
    size_name = serializers.SerializerMethodField()
    color_name = serializers.CharField(source='variant.color.color_name', read_only=True)
    shop_id = serializers.IntegerField(source='variant.product.shop.id', read_only=True)
    shop_name = serializers.CharField(source='variant.product.shop.name', read_only=True)
    product = serializers.IntegerField(source='variant.product.id', read_only=True)
    size = serializers.IntegerField(source='variant.size.id', read_only=True)
    color = serializers.IntegerField(source='variant.color.id', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'user', 'variant', 'quantity', 'unit_price', 'total_price',
            'status', 'delivery_address', 'delivery_fee', 'estimated_delivery_time',
            'deliverer', 'created_at', 'updated_at',
            'user_name', 'user_details', 'variant_details',
            'customer_name', 'product_name', 'product_id', 'size_name', 'color_name',
            'shop_id', 'shop_name', 'product', 'size', 'color',
            'delivery_option', 'payment_method', 'recipient_name', 'recipient_phone',
            'recipient_address_text', 'recipient_address_lat', 'recipient_address_lng'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_variant_details(self, obj):
        """Return complete variant information including images"""
        variant = obj.variant
        primary_image = variant.get_primary_image()
        
        return {
            'id': variant.id,
            'price': float(variant.price),
            'quantity': variant.quantity,
            'sku': variant.sku,
            'images': ProductImageDetailSerializer(variant.images.all(), many=True).data,
            'primary_image': ProductImageDetailSerializer(primary_image).data if primary_image else None,
            'size': SizeSerializer(variant.size).data if variant.size else None,
            'color': ColorSerializer(variant.color).data if variant.color else None,
            'product': {
                'id': variant.product.id,
                'name': variant.product.name,
                'description': variant.product.description,
                'category': CategorySerializer(variant.product.category).data if variant.product.category else None,
                'brand': BrandSerializer(variant.product.brand).data if variant.product.brand else None,
            },
            'shop': ShopBasicSerializer(variant.product.shop).data if variant.product.shop else None,
        }
    
    def get_user_details(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name,
        }
    
    def get_customer_name(self, obj):
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username
    
    def get_size_name(self, obj):
        if not obj.variant.size:
            return None
        return str(obj.variant.size)
    
    def validate(self, data):
        """Validate stock availability"""
        if 'variant' in data and 'quantity' in data:
            variant = data['variant']
            quantity = data['quantity']
            
            if variant.quantity < quantity:
                raise serializers.ValidationError({
                    'quantity': f'Insufficient stock. Only {variant.quantity} items available.'
                })
        return data


# ============================================================================
# SHOP SERIALIZERS
# ============================================================================

class ShopSerializer(serializers.ModelSerializer):
    """Full shop serializer"""
    location = GeometryField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    
    class Meta:
        model = Shop
        fields = ['id', 'owner', 'name', 'phone', 'email', 'address', 'location', 'latitude', 'longitude', 'description', 'is_active', 'is_verified', 'created_at', 'updated_at']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']
    
    def get_latitude(self, obj):
        return obj.latitude
    
    def get_longitude(self, obj):
        return obj.longitude


class ShopCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating shops"""
    location = GeometryField()
    
    class Meta:
        model = Shop
        fields = ['name', 'phone', 'email', 'address', 'description', 'location']


# ============================================================================
# BULK OPERATION SERIALIZERS
# ============================================================================

class BulkVariantCreateSerializer(serializers.Serializer):
    """For bulk creating variants"""
    product = serializers.IntegerField()
    variants = ProductVariantCreateSerializer(many=True)
    
    def create(self, validated_data):
        product_id = validated_data['product']
        variants_data = validated_data['variants']
        created_variants = []
        
        for variant_data in variants_data:
            variant_data['product'] = product_id
            serializer = ProductVariantCreateSerializer(data=variant_data)
            if serializer.is_valid():
                created_variants.append(serializer.save())
        return created_variants


class BulkPriceUpdateSerializer(serializers.Serializer):
    """For bulk updating variant prices"""
    updates = serializers.ListField(
        child=serializers.DictField(
            child=serializers.DecimalField(max_digits=10, decimal_places=2)
        )
    )


# ============================================================================
# STATS SERIALIZERS
# ============================================================================

class VariantStatsSerializer(serializers.Serializer):
    total_variants = serializers.IntegerField()
    active_variants = serializers.IntegerField()
    inactive_variants = serializers.IntegerField()
    out_of_stock = serializers.IntegerField()
    low_stock = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_range = serializers.DictField()


class VariantSearchSerializer(serializers.Serializer):
    """For advanced variant search"""
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
        choices=['price', '-price', 'quantity', '-quantity', 'created_at', '-created_at', 'product__name'],
        required=False
    )


# ============================================================================
# DELIVERY SERIALIZERS
# ============================================================================

class DeliverySerializer(serializers.ModelSerializer):
    """Serializer for deliveries with complete order details"""
    order_details = serializers.SerializerMethodField()
    deliverer_name = serializers.CharField(source='deliverer.username', read_only=True)
    
    class Meta:
        model = Delivery
        fields = [
            'id', 'order', 'order_details', 'deliverer', 'deliverer_name',
            'pickup_address', 'delivery_address', 'pickup_time', 'delivery_time',
            'estimated_time', 'actual_time', 'delivery_fee', 'status', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_order_details(self, obj):
        """Return complete order information"""
        order = obj.order
        variant = order.variant
        product = variant.product
        shop = product.shop
        primary_image = variant.get_primary_image()
        
        return {
            'id': order.id,
            'quantity': order.quantity,
            'unit_price': float(order.unit_price),
            'total_price': float(order.total_price),
            'status': order.status,
            'created_at': order.created_at.isoformat(),
            'delivery_option': order.delivery_option,
            'payment_method': order.payment_method,
            'recipient_name': order.recipient_name,
            'recipient_phone': order.recipient_phone,
            'user_details': {
                'id': order.user.id,
                'username': order.user.username,
                'email': order.user.email,
                'first_name': order.user.first_name,
                'last_name': order.user.last_name,
            },
            'variant_details': {
                'id': variant.id,
                'sku': variant.sku,
                'price': float(variant.price),
                'quantity': variant.quantity,
                'size': SizeSerializer(variant.size).data if variant.size else None,
                'color': ColorSerializer(variant.color).data if variant.color else None,
                'primary_image': ProductImageDetailSerializer(primary_image).data if primary_image else None,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                },
                'shop': {
                    'id': shop.id,
                    'name': shop.name,
                    'address': shop.address,
                    'phone': shop.phone,
                    'latitude': shop.latitude,
                    'longitude': shop.longitude,
                }
            }
        }


class DeliveryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating deliveries"""
    
    class Meta:
        model = Delivery
        fields = ['order', 'deliverer', 'pickup_address', 'delivery_address', 'estimated_time', 'delivery_fee', 'notes']

class ProductStatsSerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    products_with_variants = serializers.IntegerField()
    products_without_variants = serializers.IntegerField()
    variant_stats = VariantStatsSerializer()        
        
        
        
#         /*
#         from product.models import (
#     Product, Shop, Size, Color, Category, Brand, Review, Order, 
#     CartItem, WishlistItem, ProductVariant, ProductImage, Delivery
# )
# from rest_framework import serializers
# from rest_framework_gis.serializers import GeoFeatureModelSerializer, GeometryField
# # CRITICAL FIX: Add these imports for aggregation in ProductListSerializer
# from django.db.models import Avg, Min, Max, Sum


# class SizeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Size
#         fields = "__all__"
#         read_only_fields = ['id', 'created_at', 'updated_at']


# class ColorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Color
#         fields = "__all__"
#         read_only_fields = ['id', 'created_at', 'updated_at']
        
        
# class ShopBasicSerializer(serializers.ModelSerializer):
#     """Lightweight shop serializer for nested use in product listings"""
#     latitude = serializers.SerializerMethodField()
#     longitude = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Shop
#         fields = ['id', 'name', 'address', 'phone', 'latitude', 'longitude']
    
#     def get_latitude(self, obj):
#         return obj.latitude
    
#     def get_longitude(self, obj):
#         return obj.longitude


# class ProductImageBasicSerializer(serializers.ModelSerializer):
#     """Lightweight image serializer for nested use"""
#     # FIX: Add absolute URL methods
#     front_image_url = serializers.SerializerMethodField()
#     back_image_url = serializers.SerializerMethodField()
#     side_image_url = serializers.SerializerMethodField()
#     aerial_image_url = serializers.SerializerMethodField()
    
#     class Meta:
#         model = ProductImage
#         fields = ['id', 'front_image', 'back_image', 'side_image', 'aerial_image', 
#                   'front_image_url', 'back_image_url', 'side_image_url', 'aerial_image_url', 'is_primary']
    
#     def get_front_image_url(self, obj):
#         # CRITICAL FIX: Use self.context.get('request') to build the absolute URI.
#         # This prevents images from being missing or returning only local paths.
#         request = self.context.get('request')
#         if obj.front_image and request:
#             # Check for request and use build_absolute_uri
#             return request.build_absolute_uri(obj.front_image.url)
#         elif obj.front_image:
#             # Fallback for when request context is not available (e.g., local testing)
#             return obj.front_image.url
#         return None

#     def get_back_image_url(self, obj):
#         request = self.context.get('request')
#         if obj.back_image and request:
#             return request.build_absolute_uri(obj.back_image.url)
#         elif obj.back_image:
#             return obj.back_image.url
#         return None
    
#     # Repeat the same pattern for any other image fields (side_image_url, etc.)
#     def get_side_image_url(self, obj):
#         request = self.context.get('request')
#         if obj.side_image and request:
#             return request.build_absolute_uri(obj.side_image.url)
#         elif obj.side_image:
#             return obj.side_image.url
#         return None
    
#     def get_aerial_image_url(self, obj):
#         if obj.aerial_image:
#             request = self.context.get('request')
#             if request:
#                 return request.build_absolute_uri(obj.aerial_image.url)
#             return obj.aerial_image.url
#         return None


# class SizeBasicSerializer(serializers.ModelSerializer):
#     """Lightweight size serializer with display name"""
#     display = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Size
#         fields = ['id', 'size_type', 'display', 'numeric_size', 'alpha_size', 'custom_size']
    
#     def get_display(self, obj):
#         return str(obj)


# class ColorBasicSerializer(serializers.ModelSerializer):
#     """Lightweight color serializer"""
#     class Meta:
#         model = Color
#         fields = ['id', 'color_name', 'hex_code']


# class ProductVariantDetailSerializer(serializers.ModelSerializer):
#     """Detailed variant serializer with images - for use in product catalog"""
#     size = SizeBasicSerializer(read_only=True)
#     color = ColorBasicSerializer(read_only=True)
#     images = ProductImageBasicSerializer(many=True, read_only=True)
#     shop = serializers.SerializerMethodField()
    
#     class Meta:
#         model = ProductVariant
#         fields = [
#             'id', 'size', 'color', 'price', 'quantity', 
#             'sku', 'description', 'is_active', 'images','shop'
#         ]
#     def get_shop(self, obj):
#         """Get shop information from the product"""
#         if obj.product and obj.product.shop:
#             shop = obj.product.shop
#             return {
#                 'id': shop.id,
#                 'display': shop.name,  # Changed from 'name' to 'display' for consistency
#                 'phone': shop.phone,
#                 'email': shop.email,
#                 'address': shop.address,
#                 'location': {
#                     'lat': shop.latitude,
#                     'lng': shop.longitude,
#                 } if shop.location else None
#             }


# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = "__all__"
#         read_only_fields = ['id', 'created_at', 'updated_at']


# class BrandSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Brand
#         fields = "__all__"
#         read_only_fields = ['id', 'created_at', 'updated_at']


# class ProductListSerializer(serializers.ModelSerializer):
#     """
#     Enhanced product serializer that aggregates all necessary data
#     for the frontend catalog view. This is what /products/catalog returns.
#     """
#     shop_details = ShopBasicSerializer(source='shop', read_only=True)
#     image= ProductImageBasicSerializer(source="ProductImage", read_only=True)
#     category = serializers.SerializerMethodField()
#     brand = serializers.SerializerMethodField()
    
#     # Aggregated computed fields
#     avg_rating = serializers.SerializerMethodField()
#     review_count = serializers.SerializerMethodField()
#     min_price = serializers.SerializerMethodField()
#     max_price = serializers.SerializerMethodField()
#     total_stock = serializers.SerializerMethodField()
#     variant_count = serializers.SerializerMethodField()
#     primary_image_url = serializers.SerializerMethodField()
    
#     # Include full variant details with images
#     variants = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Product
#         fields = [
#             'id', 'name', 'description', 'category', 'brand',
#             'shop_details','image', 'avg_rating', 'review_count',
#             'min_price', 'max_price', 'total_stock', 'variant_count',
#             'primary_image_url', 'variants', 'is_active', 'created_at'
#         ]
    
#     def get_variants(self, obj):
#         """Get only active variants with proper context for images"""
#         active_variants = obj.variants.filter(is_active=True)
#         # Pass request context so images get absolute URLs
#         return ProductVariantDetailSerializer(
#             active_variants, 
#             many=True, 
#             context=self.context
#         ).data
    
#     def get_category(self, obj):
#         """Return category as an object with id and name"""
#         if obj.category:
#             return {
#                 'id': obj.category.id,
#                 'name': obj.category.category_name
#             }
#         return None
    
#     def get_brand(self, obj):
#         """Return brand as an object with id and name"""
#         if obj.brand:
#             return {
#                 'id': obj.brand.id,
#                 'name': obj.brand.brand_name
#             }
#         return None
    
#     def get_avg_rating(self, obj):
#         """Calculate average rating from reviews"""
#         avg = obj.reviews.aggregate(avg=Avg('rating'))['avg']
#         return round(float(avg), 1) if avg else 0.0
    
#     def get_review_count(self, obj):
#         """Get total review count"""
#         return obj.reviews.count()
    
#     def get_min_price(self, obj):
#         """Get minimum price from active variants"""
#         min_price = obj.variants.filter(is_active=True).aggregate(min=Min('price'))['min']
#         return float(min_price) if min_price else 0.0
    
#     def get_max_price(self, obj):
#         """Get maximum price from active variants"""
#         max_price = obj.variants.filter(is_active=True).aggregate(max=Max('price'))['max']
#         return float(max_price) if max_price else 0.0
    
#     def get_total_stock(self, obj):
#         """Get total stock from all active variants"""
#         total = obj.variants.filter(is_active=True).aggregate(total=Sum('quantity'))['total']
#         return int(total) if total else 0
    
#     def get_variant_count(self, obj):
#         """Get count of active variants"""
#         return obj.variants.filter(is_active=True).count()
    
#     def get_primary_image_url(self, obj):
#         """Get primary image URL - tries variant images first, then product images"""
#         request = self.context.get('request')
        
#         # Try to get primary image from variants
#         # for variant in obj.filter(is_active=True):
#         #     primary_img = variant.image.filter(is_primary=True).first()
#         #     if primary_img:
#         #         if primary_img.front_image:
#         #             return request.build_absolute_uri(primary_img.front_image.url) if request else primary_img.front_image.url
#         #         elif primary_img.back_image:
#         #             return request.build_absolute_uri(primary_img.back_image.url) if request else primary_img.back_image.url
        
#         # # Fallback to any variant image
#         # for variant in obj.variants.filter(is_active=True):
#         #     any_img = variant.image.first()
#         #     if any_img:
#         #         if any_img.front_image:
#         #             return request.build_absolute_uri(any_img.front_image.url) if request else any_img.front_image.url
#         #         elif any_img.back_image:
#         #             return request.build_absolute_uri(any_img.back_image.url) if request else any_img.back_image.url
        
#         # # Fallback to product-level image
#         # product_img = obj.image.filter(is_primary=True).first() or obj.image.first()
#         # if product_img:
#         #     if product_img.front_image:
#         #         return request.build_absolute_uri(product_img.front_image.url) if request else product_img.front_image.url
#         #     elif product_img.back_image:
#         #         return request.build_absolute_uri(product_img.back_image.url) if request else product_img.back_image.url
        
#         # return None


# class ProductVariantSerializer(serializers.ModelSerializer):
#     size_details = SizeSerializer(source='size', read_only=True)
#     color_details = ColorSerializer(source='color', read_only=True)
#     # image = ProductImageBasicSerializer(many=True, read_only=True)
    
#     class Meta:
#         model = ProductVariant
#         fields = "__all__"
#         read_only_fields = ['id', 'created_at', 'updated_at']


# class ProductImageSerializer(serializers.ModelSerializer):
#     """Full image serializer for product images"""
#     class Meta:
#         model = ProductImage
#         fields = ['id', 'front_image', 'back_image', 'side_image', 'aerial_image', 'is_primary']

# # Moving CartItemSerializer after ProductSerializer to avoid circular imports
# class ProductSerializer(serializers.ModelSerializer):
#     brand_details = BrandSerializer(source='brand', read_only=True)
#     category_details = CategorySerializer(source='category', read_only=True)
#     shop_details = ShopBasicSerializer(source='shop', read_only=True)
#     variants = ProductVariantSerializer(many=True, read_only=True)
#     image = ProductImageSerializer(source=ProductImage, read_only=True)
#     available_sizes_details = SizeSerializer(source='available_sizes', many=True, read_only=True)
#     available_colors_details = ColorSerializer(source='available_colors', many=True, read_only=True)
#     avg_rating = serializers.SerializerMethodField()
#     review_count = serializers.SerializerMethodField()
#     min_price = serializers.SerializerMethodField()
#     max_price = serializers.SerializerMethodField()
#     total_stock = serializers.SerializerMethodField()
#     variant_count = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Product
#         fields = "__all__"
#         read_only_fields = ['id', 'created_at', 'updated_at']
    
#     def get_avg_rating(self, obj):
#         reviews = obj.reviews.all()
#         if reviews:
#             return round(sum(review.rating for review in reviews) / len(reviews), 1)
#         return 0
    
#     def get_review_count(self, obj):
#         return obj.reviews.count()
    
#     def get_min_price(self, obj):
#         return obj.get_min_price()
    
#     def get_max_price(self, obj):
#         return obj.get_max_price()
    
#     def get_total_stock(self, obj):
#         return obj.get_total_stock()
    
#     def get_variant_count(self, obj):
#         return obj.variants.count()

# # Replace your CartItemSerializer in serializers.py with this version

# class CartItemSerializer(serializers.ModelSerializer):
#     variant_details = serializers.SerializerMethodField()
#     product_name = serializers.CharField(source='variant.product.name', read_only=True)
#     total_price = serializers.SerializerMethodField()
    
#     # Size and color details with proper naming
#     size_details = serializers.SerializerMethodField()
#     color_details = serializers.SerializerMethodField()
    
#     class Meta:
#         model = CartItem
#         fields = [
#             'id', 'variant', 'quantity', 'added_at', 'user',
#             'variant_details', 'total_price', 'product_name',
#             'size_details', 'color_details'
#         ]
#         read_only_fields = ['id', 'added_at', 'user']
    
#     def get_variant_details(self, obj):
#         """
#         FIX #5: Return detailed variant info including properly resolved image URLs
#         This ensures cart items display images correctly
#         """
#         variant = obj.variant
#         request = self.context.get('request')
        
#         # Get the first available image from the variant
#         first_image = variant.image.first()
        
#         # Build primary image URL with multiple fallbacks
#         primary_image_url = None
        
#         # Priority 1: Variant's front image
#         if first_image and first_image.front_image:
#             if request:
#                 primary_image_url = request.build_absolute_uri(first_image.front_image.url)
#             else:
#                 primary_image_url = first_image.front_image.url
        
#         # Priority 2: Variant's back image
#         elif first_image and first_image.back_image:
#             if request:
#                 primary_image_url = request.build_absolute_uri(first_image.back_image.url)
#             else:
#                 primary_image_url = first_image.back_image.url
        
#         # Priority 3: Product's primary image (from product.images)
#         elif variant.product.images.exists():
#             product_image = variant.product.images.first()
#             if product_image and product_image.front_image:
#                 if request:
#                     primary_image_url = request.build_absolute_uri(product_image.front_image.url)
#                 else:
#                     primary_image_url = product_image.front_image.url
        
#         # Build complete variant details response
#         return {
#             'id': variant.id,
#             'price': float(variant.price),
#             'quantity': variant.quantity,
#             'sku': variant.sku,
#             'images': [
#                 {
#                     'front_image_url': request.build_absolute_uri(img.front_image.url) if request and img.front_image else (img.front_image.url if img.front_image else None),
#                     'back_image_url': request.build_absolute_uri(img.back_image.url) if request and img.back_image else (img.back_image.url if img.back_image else None)
#                 }
#                 for img in variant.images.all()
#             ] if variant.images.exists() else [],
#             'size': {
#                 'id': variant.size.id if variant.size else None,
#                 'display': str(variant.size) if variant.size else None
#             } if variant.size else None,
#             'color': {
#                 'id': variant.color.id if variant.color else None,
#                 'name': variant.color.color_name if variant.color else None,
#                 'hex_code': variant.color.hex_code if variant.color else None
#             } if variant.color else None,
#             'product': {
#                 'id': variant.product.id,
#                 'name': variant.product.name,
#                 'primary_image_url': primary_image_url  # This is the key fix for cart images
#             },
#             'shop': {
#                 'id': variant.product.shop.id,
#                 'display': variant.product.shop.name,
#                 'phone': variant.product.shop.phone,
#                 'address': variant.product.shop.address,
#                 'location': {
#                     'lat': variant.product.shop.latitude,
#                     'lng': variant.product.shop.longitude,
#                 } if variant.product.shop.location else None
#             } if variant.product.shop else None
#         }
    
#     def get_size_details(self, obj):
#         """Return size information"""
#         if obj.variant and obj.variant.size:
#             size = obj.variant.size
#             return {
#                 'alpha_size': size.alpha_size,
#                 'numeric_size': size.numeric_size,
#                 'custom_size': size.custom_size,
#                 'display': str(size)
#             }
#         return None
    
#     def get_color_details(self, obj):
#         """Return color information"""
#         if obj.variant and obj.variant.color:
#             return {
#                 'color_name': obj.variant.color.color_name,
#                 'hex_code': obj.variant.color.hex_code
#             }
#         return None
    
#     def get_total_price(self, obj):
#         """Get price per unit (not total quantity * price)"""
#         return float(obj.variant.price) if obj.variant else 0
    
#     def validate_quantity(self, value):
#         """Validate quantity is positive"""
#         if value <= 0:
#             raise serializers.ValidationError("Quantity must be a positive number.")
#         return value
    
#     def validate(self, data):
#         """Validate that the variant has sufficient stock"""
#         if 'variant' in data and 'quantity' in data:
#             variant = data['variant']
#             quantity = data['quantity']
            
#             if variant.quantity < quantity:
#                 raise serializers.ValidationError(
#                     f"Insufficient stock. Only {variant.quantity} items available."
#                 )
        
#         return data
    
#     def create(self, validated_data):
#         """Handle duplicate cart items by merging quantities"""
#         user = self.context['request'].user
#         variant = validated_data['variant']
#         quantity = validated_data['quantity']
        
#         # Check if item already exists in cart
#         existing_item = CartItem.objects.filter(user=user, variant=variant).first()
        
#         if existing_item:
#             # Merge quantities
#             new_quantity = existing_item.quantity + quantity
            
#             # Check stock availability
#             if variant.quantity < new_quantity:
#                 raise serializers.ValidationError(
#                     f"Cannot add {quantity} more items. Only {variant.quantity - existing_item.quantity} available."
#                 )
            
#             existing_item.quantity = new_quantity
#             existing_item.save()
#             return existing_item
#         else:
#             # Create new cart item
#             return CartItem.objects.create(user=user, variant=variant, quantity=quantity)


# # Add remaining serializers (keeping your originals)
# class ProductVariantSerializer(serializers.ModelSerializer):
#     size = SizeSerializer(read_only=True)
#     color = ColorSerializer(read_only=True)
#     image = ProductImageBasicSerializer(read_only=True)
    
# # Now define ProductSerializer after ProductImageSerializer
#     """Full image serializer for product images"""
#     class Meta:
#         model = ProductVariant
#         fields = [ 
#             'id', 'product', 'sku', 'price', 'quantity', 
#             'is_active', 'size', 'color', 
#             'created_at', 'updated_at',
#             'image' # <-- ADDED THIS FIELD
#         ]
#         read_only_fields = ['id', 'created_at', 'updated_at']

# # Now define ProductSerializer after ProductImageSerializer
# class ProductSerializer(serializers.ModelSerializer):
#     brand_details = BrandSerializer(source='brand', read_only=True)
#     category_details = CategorySerializer(source='category', read_only=True)
#     shop_details = ShopBasicSerializer(source='shop', read_only=True)
#     variants = ProductVariantSerializer(many= True, read_only=True)
#     image = ProductImageSerializer(source="ProductImage", read_only=True)
#     available_sizes_details = SizeSerializer(source='available_sizes', many=True, read_only=True)
#     available_colors_details = ColorSerializer(source='available_colors', many=True, read_only=True)
#     avg_rating = serializers.SerializerMethodField()
#     review_count = serializers.SerializerMethodField()
#     min_price = serializers.SerializerMethodField()
#     max_price = serializers.SerializerMethodField()
#     total_stock = serializers.SerializerMethodField()
#     variant_count = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Product
#         fields = "__all__"
#         read_only_fields = ['id', 'created_at', 'updated_at']
    
#     def get_avg_rating(self, obj):
#         reviews = obj.reviews.all()
#         if reviews:
#             return round(sum(review.rating for review in reviews) / len(reviews), 1)
#         return 0
    
#     def get_review_count(self, obj):
#         return obj.reviews.count()
    
#     def get_min_price(self, obj):
#         return obj.get_min_price()
    
#     def get_max_price(self, obj):
#         return obj.get_max_price()
    
#     def get_total_stock(self, obj):
#         return obj.get_total_stock()
    
#     def get_variant_count(self, obj):
#         return obj.variants.count()


# class ReviewSerializer(serializers.ModelSerializer):
#     user_name = serializers.CharField(source='user.username', read_only=True)
#     product_name = serializers.CharField(source='product.name', read_only=True)
#     variant_details = ProductVariantSerializer(source='variant', read_only=True)
    
#     class Meta:
#         model = Review
#         fields = "__all__"
#         read_only_fields = ['id', 'created_at', 'updated_at', 'user']
        
#     def validate_rating(self, value):
#         if value < 1 or value > 5:
#             raise serializers.ValidationError("Rating must be between 1 and 5.")
#         return value


# class OrderSerializer(serializers.ModelSerializer):
#     user_name = serializers.CharField(source='user.username', read_only=True)
#     user_details = serializers.SerializerMethodField()
    
#     # FIX #2: Include complete variant details with images and product info
#     variant_details = serializers.SerializerMethodField()
    
#     customer_name = serializers.SerializerMethodField()
#     product_name = serializers.CharField(source='variant.product.name', read_only=True)
#     product_id = serializers.IntegerField(source='variant.product.id', read_only=True)
#     size_name = serializers.SerializerMethodField()
#     color_name = serializers.CharField(source='variant.color.color_name', read_only=True)
#     shop_id = serializers.IntegerField(source='variant.product.shop.id', read_only=True)
#     shop_name = serializers.CharField(source='variant.product.shop.name', read_only=True)
#     product = serializers.IntegerField(source='variant.product.id', read_only=True)
#     size = serializers.IntegerField(source='variant.size.id', read_only=True)
#     color = serializers.IntegerField(source='variant.color.id', read_only=True)
    
#     class Meta:
#         model = Order
#         fields = [
#             'id', 'user', 'variant', 'quantity', 'unit_price', 'total_price',
#             'status', 'delivery_address', 'delivery_fee', 'estimated_delivery_time',
#             'deliverer', 'created_at', 'updated_at',
#             'user_name', 'user_details', 'variant_details',
#             'customer_name', 'product_name', 'product_id', 'size_name', 'color_name',
#             'shop_id', 'shop_name', 'product', 'size', 'color',
#             'delivery_option', 'payment_method', 'recipient_name', 'recipient_phone',
#             'recipient_address_text', 'recipient_address_lat', 'recipient_address_lng'
#         ]
#         read_only_fields = ['id','user', 'created_at', 'updated_at']
    
#     def get_variant_details(self, obj):
#         """Return complete variant information including images"""
#         variant = obj.variant
#         request = self.context.get('request')
        
#         return {
#             'id': variant.id,
#             'price': float(variant.price),
#             'quantity': variant.quantity,
#             'sku': variant.sku,
#             'image': [
#                 {
#                     'front_image_url': request.build_absolute_uri(img.front_image.url) if request and img.front_image else img.front_image.url if img.front_image else None,
#                     'back_image_url': request.build_absolute_uri(img.back_image.url) if request and img.back_image else img.back_image.url if img.back_image else None,
#                     'side_image_url': request.build_absolute_uri(img.side_image.url) if request and img.side_image else img.side_image.url if img.side_image else None,
#                     'aerial_image_url': request.build_absolute_uri(img.aerial_image.url) if request and img.aerial_image else img.aerial_image.url if img.aerial_image else None,
#                     'is_primary': img.is_primary,
#                 }
#                 for img in variant.images.all()
#             ] if variant.images.exists() else [],
#             'size': {
#                 'id': variant.size.id if variant.size else None,
#                 'display': str(variant.size) if variant.size else None,
#                 'alpha_size': variant.size.alpha_size if variant.size else None,
#                 'numeric_size': variant.size.numeric_size if variant.size else None
#             } if variant.size else None,
#             'color': {
#                 'id': variant.color.id if variant.color else None,
#                 'name': variant.color.color_name if variant.color else None,
#                 'hex_code': variant.color.hex_code if variant.color else None
#             } if variant.color else None,
#             'product': {
#                 'id': variant.product.id,
#                 'name': variant.product.name,
#                 'description': variant.product.description,
#                 'category': {
#                     'id': variant.product.category.id,
#                     'name': variant.product.category.category_name
#                 } if variant.product.category else None,
#                 'brand': {
#                     'id': variant.product.brand.id,
#                     'name': variant.product.brand.brand_name
#                 } if variant.product.brand else None
#             },
#             'shop': {
#                 'id': variant.product.shop.id,
#                 'name': variant.product.shop.name,
#                 'address': variant.product.shop.address,
#                 'phone': variant.product.shop.phone,
#                 'location': {
#                     'lat': variant.product.shop.latitude,
#                     'lng': variant.product.shop.longitude,
#                 } if variant.product.shop.location else None
#             } if variant.product.shop else None
#         }
    
#     def get_user_details(self, obj):
#         user = obj.user
#         return {
#             'id': user.id,
#             'username': user.username,
#             'email': user.email,
#             'first_name': user.first_name,
#             'last_name': user.last_name,
#         }
    
#     def get_customer_name(self, obj):
#         user = obj.user
#         if user.first_name and user.last_name:
#             return f"{user.first_name} {user.last_name}"
#         return user.username
    
#     def get_size_name(self, obj):
#         size = obj.variant.size
#         if not size:
#             return None
#         if size.size_type == 'numeric' and size.numeric_size:
#             return str(size.numeric_size)
#         elif size.size_type == 'alpha' and size.alpha_size:
#             return size.alpha_size
#         elif size.size_type == 'custom' and size.custom_size:
#             return size.custom_size
#         return f"Size {size.id}"
    
#     def validate(self, data):
#         """Validate stock availability before creating order"""
#         if 'variant' in data and 'quantity' in data:
#             variant = data['variant']
#             quantity = data['quantity']
            
#             if variant.quantity < quantity:
#                 raise serializers.ValidationError({
#                     'quantity': f'Insufficient stock. Only {variant.quantity} items available.'
#                 })
        
#         return data


# # Replace the WishlistItemSerializer in your serializers.py with this fixed version

# class WishlistItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.CharField(source='product.name', read_only=True)
#     product_details = serializers.SerializerMethodField()
    
#     class Meta:
#         model = WishlistItem
#         fields = ['id', 'product', 'product_name', 'product_details', 'added_at', 'user']
#         read_only_fields = ['id', 'added_at', 'user']
    
#     def get_product_details(self, obj):
#         """Return complete product information for wishlist display"""
#         product = obj.product
#         request = self.context.get('request')
        
#         # Calculate min/max prices from variants
#         variants = product.variants.all()
#         prices = [v.price for v in variants if v.is_active]
#         min_price = min(prices) if prices else 0
#         max_price = max(prices) if prices else 0
#         total_stock = sum(v.quantity for v in variants if v.is_active)
#         image= ProductImageBasicSerializer(source="ProductImage", read_only=True)
        
#         # Get primary image
#         primary_image_url = None
#         if product.variants.exists():
#             first_variant = product.variants.first()
#             if first_variant and first_variant.images.exists():
#                 first_image = first_variant.images.first()
#                 if first_image and first_image.front_image:
#                     if request:
#                         primary_image_url = request.build_absolute_uri(first_image.front_image.url)
#                     else:
#                         primary_image_url = first_image.front_image.url
        
#         # Calculate average rating
#         reviews = product.reviews.all()
#         avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
#         review_count = reviews.count()
        
#         return {
#             'id': product.id,
#             'name': product.name,
#             'description': product.description,
#             'image': "hhhhhhhh",
#             'min_price': float(min_price),
#             'max_price': float(max_price),
#             'total_stock': total_stock,
#             'avg_rating': round(float(avg_rating), 1) if avg_rating else 0.0,
#             'review_count': review_count,
#             'primary_image_url': primary_image_url,
#             'category': {
#                 'id': product.category.id,
#                 'name': product.category.category_name
#             } if product.category else None,
#             'brand': {
#                 'id': product.brand.id,
#                 'name': product.brand.brand_name
#             } if product.brand else None,
#             'is_active': product.is_active,
#         }


# # In serializers.py (find this class and ensure it includes 'id')
# class ProductCreateSerializer(serializers.ModelSerializer):
#     """Serializer used for Product creation."""
    
#     # Optional: If you want to use the standard ProductSerializer fields 
#     # for the successful response, you can define it like this.
#     # However, for simplicity and explicit control over input/output:
    
#     class Meta:
#         model = Product
#         # Include 'id' so it is serialized back to the frontend on successful creation.
#         fields = [
#             'id', 'name', 'description', 'brand', 'category', 
#             'is_active', 'shop', 'created_at', 'updated_at'
#         ]
#         # These fields should be read-only if they are generated by Django/DB
#         read_only_fields = ['id', 'created_at', 'updated_at']
        
#         # Ensure 'shop', 'brand', and 'category' are required for creation
#         extra_kwargs = {
#             'shop': {'required': True},
#             'category': {'required': True},
#             'brand': {'required': True},
#         }

# # Note: The DRF ModelViewSet's default .create() method automatically uses 
# # the serializer's .save() result (the created model instance) to re-serialize 
# # the response data. Including 'id' in the fields list is typically sufficient.

# class ShopSerializer(serializers.ModelSerializer):
#     location = GeometryField()
    
#     class Meta:
#         model = Shop
#         fields = "__all__"
#         read_only_fields = ['id', 'created_at', 'updated_at']


# class ProductVariantCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductVariant
#         fields = ['product', 'size', 'color', 'price', 'quantity', 'sku', 'description', 'is_active']


# class ShopCreateSerializer(serializers.ModelSerializer):
#     location = GeometryField()
    
#     class Meta:
#         model = Shop
#         fields = ['name', 'phone', 'email', 'address', 'description', 'location']


# class BulkVariantCreateSerializer(serializers.Serializer):
#     product = serializers.IntegerField()
#     variants = ProductVariantCreateSerializer(many=True)
    
#     def create(self, validated_data):
#         product_id = validated_data['product']
#         variants_data = validated_data['variants']
#         created_variants = []
#         for variant_data in variants_data:
#             variant_data['product'] = product_id
#             serializer = ProductVariantCreateSerializer(data=variant_data)
#             if serializer.is_valid():
#                 created_variants.append(serializer.save())
#         return created_variants


# class BulkPriceUpdateSerializer(serializers.Serializer):
#     updates = serializers.ListField(
#         child=serializers.DictField(
#             child=serializers.DecimalField(max_digits=10, decimal_places=2)
#         )
#     )


# class VariantStatsSerializer(serializers.Serializer):
#     total_variants = serializers.IntegerField()
#     active_variants = serializers.IntegerField()
#     inactive_variants = serializers.IntegerField()
#     out_of_stock = serializers.IntegerField()
#     low_stock = serializers.IntegerField()
#     total_value = serializers.DecimalField(max_digits=12, decimal_places=2)
#     average_price = serializers.DecimalField(max_digits=10, decimal_places=2)
#     price_range = serializers.DictField()


# class ProductStatsSerializer(serializers.Serializer):
#     total_products = serializers.IntegerField()
#     active_products = serializers.IntegerField()
#     products_with_variants = serializers.IntegerField()
#     products_without_variants = serializers.IntegerField()
#     variant_stats = VariantStatsSerializer()


# class VariantSearchSerializer(serializers.Serializer):
#     search = serializers.CharField(required=False, allow_blank=True)
#     shop = serializers.IntegerField(required=False)
#     category = serializers.IntegerField(required=False)
#     brand = serializers.IntegerField(required=False)
#     size = serializers.IntegerField(required=False)
#     color = serializers.IntegerField(required=False)
#     min_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
#     max_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
#     in_stock = serializers.BooleanField(required=False)
#     is_active = serializers.BooleanField(required=False)
#     ordering = serializers.ChoiceField(
#         choices=['price', '-price', 'quantity', '-quantity', 'created_at', '-created_at', 'product__name'],
#         required=False
#     )


# # Add this to your serializers.py - REPLACE the existing DeliverySerializer

# class DeliverySerializer(serializers.ModelSerializer):
#     """
#     Enhanced DeliverySerializer with complete order details
#     """
#     order_details = serializers.SerializerMethodField()
#     deliverer_name = serializers.CharField(source='deliverer.username', read_only=True)
    
#     class Meta:
#         model = Delivery
#         fields = [
#             'id', 'order', 'order_details', 'deliverer', 'deliverer_name',
#             'pickup_address', 'delivery_address', 'pickup_time', 'delivery_time',
#             'estimated_time', 'actual_time', 'delivery_fee', 'status', 'notes',
#             'created_at', 'updated_at'
#         ]
#         read_only_fields = ['created_at', 'updated_at']
    
#     def get_order_details(self, obj):
#         """Return complete order information with nested variant and product details"""
#         order = obj.order
#         request = self.context.get('request')
        
#         # Get variant details
#         variant = order.variant
#         product = variant.product
#         shop = product.shop
        
#         # Get first image
#         first_image = variant.images.first()
#         product_image_url = None
        
#         if first_image and first_image.front_image:
#             if request:
#                 product_image_url = request.build_absolute_uri(first_image.front_image.url)
#             else:
#                 product_image_url = first_image.front_image.url
#         elif first_image and first_image.back_image:
#             if request:
#                 product_image_url = request.build_absolute_uri(first_image.back_image.url)
#             else:
#                 product_image_url = first_image.back_image.url
        
#         return {
#             'id': order.id,
#             'quantity': order.quantity,
#             'unit_price': float(order.unit_price),
#             'total_price': float(order.total_price),
#             'status': order.status,
#             'created_at': order.created_at.isoformat(),
#             'delivery_option': order.delivery_option,
#             'payment_method': order.payment_method,
#             'recipient_name': order.recipient_name,
#             'recipient_phone': order.recipient_phone,
#             'user_details': {
#                 'id': order.user.id,
#                 'username': order.user.username,
#                 'email': order.user.email,
#                 'first_name': order.user.first_name,
#                 'last_name': order.user.last_name,
#             },
#             'variant_details': {
#                 'id': variant.id,
#                 'sku': variant.sku,
#                 'price': float(variant.price),
#                 'quantity': variant.quantity,
#                 'size_details': {
#                     'id': variant.size.id if variant.size else None,
#                     'size_name': str(variant.size) if variant.size else None,
#                 } if variant.size else None,
#                 'color_details': {
#                     'id': variant.color.id if variant.color else None,
#                     'color_name': variant.color.color_name if variant.color else None,
#                     'hex_code': variant.color.hex_code if variant.color else None,
#                 } if variant.color else None,
#                 'product_details': {
#                     'id': product.id,
#                     'name': product.name,
#                     'description': product.description,
#                     'image_url': product_image_url,
#                     'shop': {
#                         'id': shop.id,
#                         'name': shop.name,
#                         'address': shop.address,
#                         'phone': shop.phone,
#                         'latitude': shop.latitude,
#                         'longitude': shop.longitude,
#                     }
#                 }
#             }
#         }


# class DeliveryCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Delivery
#         fields = ['order', 'deliverer', 'pickup_address', 'delivery_address', 'estimated_time', 'delivery_fee', 'notes']
#         */