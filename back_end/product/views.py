from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Avg, Count, Min, Max
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta, datetime, time
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from product.models import (
    Product, Shop, Size, Color, Category, Brand, Review, Order, 
    CartItem, WishlistItem, ProductVariant, ProductImage, Delivery,SubCategory
)
from .serializers import (
    ProductSerializer, ShopSerializer, SizeSerializer, ColorSerializer,
    CategorySerializer, BrandSerializer, ReviewSerializer, OrderSerializer,
    CartItemSerializer, WishlistItemSerializer, ProductVariantSerializer,
    ProductImageSerializer, ProductCreateSerializer, ProductVariantCreateSerializer,
    BulkVariantCreateSerializer, BulkPriceUpdateSerializer, VariantStatsSerializer,
    ProductStatsSerializer, VariantSearchSerializer, DeliverySerializer, DeliveryCreateSerializer , ProductListSerializer,ShopCreateSerializer,SubCategorySerializer)



# NEW: Custom Pagination Class (Request #1)
class StandardResultsPagination(PageNumberPagination):
    # Set a default page size and allow client to override
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    pagination_class = StandardResultsPagination  # Use custom pagination
    filterset_fields = ['shop', 'category', 'brand', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Allow anyone to view products (list, retrieve)
        Require authentication for modifications (create, update, delete)
        """
        if self.action in ['list', 'retrieve', 'variants', 'stats', 'catalog']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Use ProductListSerializer for catalog, keep others as-is"""
        if self.action == 'catalog':  # NEW: Use enhanced serializer for catalog
            return ProductListSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        elif self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_serializer_context(self):
        """
        Passes the request context to the serializer.
        This is necessary for SerializerMethodFields (like image_url) 
        to build absolute URIs.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        """
        ENHANCED: Added subcategory filtering support
        """
        # Add prefetch for better performance
        queryset = Product.objects.filter(is_active=True).order_by('-created_at')
        queryset = queryset.annotate(
            min_price=Min('variants__price'),
            max_price=Max('variants__price'),
            total_stock=Sum('variants__quantity')
        ).distinct()
        
        # Annotate with average rating
        queryset = queryset.annotate(
            avg_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )
        
        # Add select_related for subcategory
        queryset = queryset.select_related('category', 'subcategory', 'brand', 'shop')
        
        # Keep your existing permission logic exactly as-is
        if self.request.user.is_staff:
            return queryset
        
        if self.request.user.is_authenticated:
            user_shops = Shop.objects.filter(owner=self.request.user)
            
            if user_shops.exists():
                queryset = queryset.filter(shop__in=user_shops)
            else:
                queryset = queryset.filter(is_active=True)
        else:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    
    @action(detail=True, methods=['post'], parser_classes=(MultiPartParser, FormParser))
    def upload_images(self, request, pk=None):
        """
        FIXED: Upload images and link them to a specific variant
        Expects: variant_id in the request data
        """
        product = self.get_object()
        
        # Get the variant ID from request
        variant_id = request.data.get('variant_id')
        
        if not variant_id:
            return Response(
                {'detail': 'variant_id is required to upload images'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify the variant belongs to this product
        try:
            variant = ProductVariant.objects.get(id=variant_id, product=product)
        except ProductVariant.DoesNotExist:
            return Response(
                {'detail': 'Variant not found for this product'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Gather the four image files
        front_image = request.FILES.get('front_image')
        back_image = request.FILES.get('back_image')
        side_image = request.FILES.get('side_image')
        aerial_image = request.FILES.get('aerial_image')
        
        # At least one image is required
        if not any([front_image, back_image, side_image, aerial_image]):
            return Response(
                {'detail': 'At least one image is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Construct the data for ProductImage
        data = {
            'variant': variant.id,  # Link to the variant, not product
            'front_image': front_image,
            'back_image': back_image,
            'side_image': side_image,
            'aerial_image': aerial_image,
            'is_primary': request.data.get('is_primary', False)
        }
        
        # Use ProductImageSerializer to validate and save
        serializer = ProductImageSerializer(data=data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
    
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def catalog(self, request):
        """
        ENHANCED: Added subcategory filtering
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply additional filters from query params
        category = request.query_params.get('category')
        subcategory = request.query_params.get('subcategory')  # NEW
        brand = request.query_params.get('brand')
        min_price = request.query_params.get('min_price')
        max_price = request.query_params.get('max_price')
        in_stock = request.query_params.get('in_stock')
        
        # Filter by category
        if category and category != 'All':
            try:
                queryset = queryset.filter(category_id=int(category))
            except (ValueError, TypeError):
                pass
        
        # NEW: Filter by subcategory
        if subcategory and subcategory != 'All':
            try:
                queryset = queryset.filter(subcategory_id=int(subcategory))
            except (ValueError, TypeError):
                pass
        
        # Filter by brand
        if brand and brand != 'All':
            try:
                queryset = queryset.filter(brand_id=int(brand))
            except (ValueError, TypeError):
                pass
        
        # Filter by price range
        if min_price or max_price:
            from django.db.models import Min as DbMin
            queryset = queryset.annotate(
                min_variant_price=DbMin('variants__price')
            )
            if min_price:
                try:
                    queryset = queryset.filter(min_variant_price__gte=float(min_price))
                except (ValueError, TypeError):
                    pass
            if max_price:
                try:
                    queryset = queryset.filter(min_variant_price__lte=float(max_price))
                except (ValueError, TypeError):
                    pass
        
        # Filter by stock availability
        if in_stock == 'true':
            queryset = queryset.annotate(
                total_quantity=Sum('variants__quantity')
            ).filter(total_quantity__gt=0)
        
        # Prefetch images
        queryset = queryset.prefetch_related(
            'variants',
            'variants__size',
            'variants__color',
            'variants__product__shop',
            'category',
            'subcategory',  # NEW
            'brand',
            'shop'
        )
        
        # Use pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def variants(self, request, pk=None):
        """Get all variants for a specific product"""
        product = self.get_object()
        variants = ProductVariant.objects.filter(product=product).select_related(
            'size', 'color'
        )
        serializer = ProductVariantSerializer(variants, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_variant(self, request, pk=None):
        """Add a variant to a specific product"""
        product = self.get_object()
        data = request.data.copy()
        data['product'] = product.id
        
        serializer = ProductVariantCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def bulk_add_variants(self, request, pk=None):
        """Add multiple variants to a product at once"""
        product = self.get_object()
        data = {
            'product': product.id,
            'variants': request.data.get('variants', [])
        }
        
        serializer = BulkVariantCreateSerializer(data=data)
        if serializer.is_valid():
            variants = serializer.save()
            variant_serializer = ProductVariantSerializer(variants, many=True)
            return Response(variant_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_size(self, request, pk=None):
        """Add a size to product's available sizes"""
        product = self.get_object()
        size_id = request.data.get('size_id')
        
        try:
            size = Size.objects.get(id=size_id)
            
            # Validate size type matches category
            if product.category and size.size_type != product.category.size_type:
                return Response(
                    {'error': f'Size type must be {product.category.size_type}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            product.available_sizes.add(size)
            return Response({'message': 'Size added successfully'})
        except Size.DoesNotExist:
            return Response({'error': 'Size not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_size(self, request, pk=None):
        """Remove a size from product's available sizes"""
        product = self.get_object()
        size_id = request.data.get('size_id')
        
        try:
            size = Size.objects.get(id=size_id)
            product.available_sizes.remove(size)
            # Optionally delete variants with this size
            if request.data.get('delete_variants', False):
                ProductVariant.objects.filter(product=product, size=size).delete()
            return Response({'message': 'Size removed successfully'})
        except Size.DoesNotExist:
            return Response({'error': 'Size not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def add_color(self, request, pk=None):
        """Add a color to product's available colors"""
        product = self.get_object()
        color_id = request.data.get('color_id')
        
        try:
            color = Color.objects.get(id=color_id)
            product.available_colors.add(color)
            return Response({'message': 'Color added successfully'})
        except Color.DoesNotExist:
            return Response({'error': 'Color not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_color(self, request, pk=None):
        """Remove a color from product's available colors"""
        product = self.get_object()
        color_id = request.data.get('color_id')
        
        try:
            color = Color.objects.get(id=color_id)
            product.available_colors.remove(color)
            # Optionally delete variants with this color
            if request.data.get('delete_variants', False):
                ProductVariant.objects.filter(product=product, color=color).delete()
            return Response({'message': 'Color removed successfully'})
        except Color.DoesNotExist:
            return Response({'error': 'Color not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a specific product"""
        product = self.get_object()
        variants = product.variants.all()
        
        stats = {
            'total_variants': variants.count(),
            'active_variants': variants.filter(is_active=True).count(),
            'total_stock': variants.aggregate(total=Sum('quantity'))['total'] or 0,
            'out_of_stock': variants.filter(quantity=0).count(),
            'low_stock': variants.filter(quantity__lte=10, quantity__gt=0).count(),
            'price_range': {
                'min': variants.aggregate(min_price=Min('price'))['min_price'],
                'max': variants.aggregate(max_price=Max('price'))['max_price']
            },
            'average_price': variants.aggregate(avg_price=Avg('price'))['avg_price']
        }
        
        return Response(stats)


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination  # Use custom pagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'size', 'color', 'is_active', 'product__shop', 'product__category']
    search_fields = ['product__name', 'sku', 'description']
    ordering_fields = ['price', 'quantity', 'created_at']
    ordering = ['-created_at']
    
    
    def get_permissions(self):
        """Allow read-only access for unauthenticated users"""
        if self.action in ['list', 'retrieve', 'search', 'stats']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProductVariantCreateSerializer
        return ProductVariantSerializer
    
    def get_queryset(self):
        """
        FIXED: Use prefetch_related for 'images' (reverse relation)
        Keeps all your existing permission logic
        """
        queryset = ProductVariant.objects.select_related(
            'product', 
            'product__shop', 
            'product__shop__owner',
            'product__category', 
            'product__brand', 
            'size', 
            'color'
        ).prefetch_related(
            'images',  # FIXED: Changed from select_related to prefetch_related
            'product__reviews'
        )
        
        # Staff sees everything
        if self.request.user.is_staff:
            print("Staff user - returning all")
            return queryset

        # For authenticated users, check if they are sellers
        if self.request.user.is_authenticated:
            user_shops = Shop.objects.filter(owner=self.request.user)
            print(f"User shops count: {user_shops.count()}")
        
            # Sellers see only their shop's variants
            if user_shops.exists():
                filtered = queryset.filter(product__shop__in=user_shops)
                print(f"Seller - filtered to their shops: {filtered.count()}")
                return filtered
            # Customers see all active variants
            else:
                filtered = queryset.filter(is_active=True, product__is_active=True)
                print(f"Customer - filtered active: {filtered.count()}")
                return filtered
        else:
            # Anonymous users see all active variants
            filtered = queryset.filter(is_active=True, product__is_active=True)
            print(f"Anonymous - filtered active: {filtered.count()}")
            print("=" * 50)
            return filtered
    
    @action(detail=False, methods=['post'])
    def bulk_update_prices(self, request):
        """Bulk update prices for multiple variants"""
        serializer = BulkPriceUpdateSerializer(data=request.data)
        if serializer.is_valid():
            updates = serializer.validated_data['updates']
            updated_variants = []
            
            for update in updates:
                try:
                    variant = ProductVariant.objects.get(id=update['id'])
                    # Check permission
                    if not request.user.is_staff and variant.product.shop.owner != request.user:
                        continue
                        
                    variant.price = update['price']
                    variant.save()
                    updated_variants.append(variant)
                except ProductVariant.DoesNotExist:
                    continue
            
            result_serializer = ProductVariantSerializer(updated_variants, many=True)
            return Response({
                'message': f'Updated {len(updated_variants)} variants',
                'updated_variants': result_serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get variants with low stock"""
        threshold = int(request.query_params.get('threshold', 10))
        queryset = self.get_queryset().filter(
            quantity__lte=threshold, 
            quantity__gt=0,
            is_active=True
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get variants that are out of stock"""
        queryset = self.get_queryset().filter(quantity=0, is_active=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Advanced search for variants"""
        search_serializer = VariantSearchSerializer(data=request.query_params)
        if not search_serializer.is_valid():
            return Response(search_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        filters = search_serializer.validated_data
        queryset = self.get_queryset()
        
        # Apply search filters
        if filters.get('search'):
            queryset = queryset.filter(
                Q(product__name__icontains=filters['search']) |
                Q(sku__icontains=filters['search']) |
                Q(description__icontains=filters['search'])
            )
        
        if filters.get('shop'):
            queryset = queryset.filter(product__shop_id=filters['shop'])
        
        if filters.get('category'):
            queryset = queryset.filter(product__category_id=filters['category'])
        
        if filters.get('brand'):
            queryset = queryset.filter(product__brand_id=filters['brand'])
        
        if filters.get('size'):
            queryset = queryset.filter(size_id=filters['size'])
        
        if filters.get('color'):
            queryset = queryset.filter(color_id=filters['color'])
        
        if filters.get('min_price'):
            queryset = queryset.filter(price__gte=filters['min_price'])
        
        if filters.get('max_price'):
            queryset = queryset.filter(price__lte=filters['max_price'])
        
        if filters.get('in_stock') is not None:
            if filters['in_stock']:
                queryset = queryset.filter(quantity__gt=0)
            else:
                queryset = queryset.filter(quantity=0)
        
        if filters.get('is_active') is not None:
            queryset = queryset.filter(is_active=filters['is_active'])
        
        if filters.get('ordering'):
            queryset = queryset.order_by(filters['ordering'])
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get overall variant statistics"""
        queryset = self.get_queryset()
        
        total_value = 0
        for variant in queryset:
            total_value += variant.price * variant.quantity
        
        stats = {
            'total_variants': queryset.count(),
            'active_variants': queryset.filter(is_active=True).count(),
            'inactive_variants': queryset.filter(is_active=False).count(),
            'out_of_stock': queryset.filter(quantity=0).count(),
            'low_stock': queryset.filter(quantity__lte=10, quantity__gt=0).count(),
            'total_value': total_value,
            'average_price': queryset.aggregate(avg=Avg('price'))['avg'] or 0,
            'price_range': {
                'min': queryset.aggregate(min=Min('price'))['min'],
                'max': queryset.aggregate(max=Max('price'))['max']
            }
        }
        
        return Response(stats)


class SizeViewSet(viewsets.ModelViewSet):
    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['size_type']
    ordering_fields = ['size_type', 'numeric_size', 'alpha_size', 'created_at']
    ordering = ['size_type', 'numeric_size', 'alpha_size']
    
    def get_permissions(self):
        """Allow read for all, require auth for create/update/delete"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get sizes compatible with a specific category"""
        category_id = request.query_params.get('category')
        if not category_id:
            return Response({'error': 'Category ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = Category.objects.get(id=category_id)
            sizes = Size.objects.filter(size_type=category.size_type)
            serializer = self.get_serializer(sizes, many=True)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)


class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['color_name']
    ordering_fields = ['color_name', 'created_at']
    ordering = ['color_name']
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['category_name', 'description']
    ordering_fields = ['category_name', 'created_at']
    ordering = ['category_name']
    
    def get_permissions(self):
        """Allow read-only access for unauthenticated users"""
        if self.action in ['list', 'retrieve', 'compatible_sizes', 'subcategories']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['get'])
    def compatible_sizes(self, request, pk=None):
        """Get sizes compatible with this category"""
        category = self.get_object()
        sizes = Size.objects.filter(size_type=category.size_type)
        serializer = SizeSerializer(sizes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subcategories(self, request, pk=None):
        """Get all subcategories for this category"""
        category = self.get_object()
        subcategories = category.subcategories.all()
        serializer = SubCategorySerializer(subcategories, many=True)
        return Response({
            'category': {
                'id': category.id,
                'name': category.category_name,
                'size_type': category.size_type
            },
            'subcategories': serializer.data,
            'count': subcategories.count()
        })

class SubCategoryViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category']  # Filter subcategories by category
    search_fields = ['subcategory_name', 'description']
    ordering_fields = ['subcategory_name', 'created_at']
    ordering = ['subcategory_name']
    
    def get_permissions(self):
        """Allow read-only access for unauthenticated users"""
        if self.action in ['list', 'retrieve', 'by_category']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get subcategories for a specific category"""
        category_id = request.query_params.get('category')
        if not category_id:
            return Response(
                {'error': 'Category ID is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            category = Category.objects.get(id=category_id)
            subcategories = SubCategory.objects.filter(category=category)
            serializer = self.get_serializer(subcategories, many=True)
            return Response({
                'category': {
                    'id': category.id,
                    'name': category.category_name
                },
                'subcategories': serializer.data
            })
        except Category.DoesNotExist:
            return Response(
                {'error': 'Category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['brand_name', 'description']
    ordering_fields = ['brand_name', 'created_at']
    ordering = ['brand_name']
    
    def get_permissions(self):
        """Allow read-only access for unauthenticated users"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = Brand.objects.all()
    
        # Staff sees all brands
        if self.request.user.is_staff:
            return queryset
    
        # For authenticated sellers with shops, filter brands by their products
        if self.request.user.is_authenticated:
            user_shops = Shop.objects.filter(owner=self.request.user)
        
            if user_shops.exists():
                # Sellers see brands used in their shops
                queryset = queryset.filter(products__shop__in=user_shops).distinct()
            # Customers and anonymous users see all brands
    
        return queryset
    
    def perform_create(self, serializer):
        # Prevent creating duplicate brands
        brand_name = serializer.validated_data.get('brand_name')
        if Brand.objects.filter(brand_name__iexact=brand_name).exists():
            raise BrandSerializer.ValidationError("Brand with this name already exists.")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Prevent deletion if brand has associated products
        if instance.products.exists():
            raise BrandSerializer.ValidationError("Cannot delete brand with associated products.")
        instance.delete()
    
    def perform_update(self, serializer):
        # Prevent changing brand name to an existing brand's name
        new_name = serializer.validated_data.get('brand_name', instance.brand_name)
        if Brand.objects.exclude(id=serializer.instance.id).filter(brand_name=new_name).exists():
            raise BrandSerializer.ValidationError("Brand name must be unique.")
        serializer.save()



class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product', 'variant', 'color', 'is_primary']
    
    def get_queryset(self):
        queryset = ProductImage.objects.select_related('product', 'variant', 'color')
        
        # Filter by user's shops if not admin
        if not self.request.user.is_staff:
            user_shops = Shop.objects.filter(owner=self.request.user)
            queryset = queryset.filter(product__shop__in=user_shops)
            
        return queryset


class ShopViewSet(viewsets.ModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination  # Use custom pagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'address']
    ordering_fields = ['name', 'created_at']
    ordering = ['-created_at']
    def get_permissions(self):

        """Allow anyone to view shops and nearby search, require auth for modifications."""
        if self.action in ['list', 'retrieve', 'nearby']:

            permission_classes = [AllowAny]

        else:

            # my_shops REQUIRES authentication - this was the bug

            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]



    @action(detail=False, methods=['get'])

    def my_shops(self, request):

        """Get the current user's shops with improved error handling."""

        try:

            # Debug: Log the user info

            print(f"DEBUG: User authenticated: {request.user.is_authenticated}")

            print(f"DEBUG: User: {request.user}")

            print(f"DEBUG: User ID: {request.user.id if request.user.is_authenticated else 'None'}")

            

            if not request.user.is_authenticated:

                return Response(

                    {'message': 'Authentication required', 'error': 'User not authenticated'},

                    status=status.HTTP_401_UNAUTHORIZED

                )

            

            # Look up the shop using the owner field

            shops = Shop.objects.filter(owner=request.user).order_by('-created_at')

            

            print(f"DEBUG: Found {shops.count()} shops for user {request.user.id}")

            

            if not shops.exists():

                return Response(

                    {

                        'message': 'No shops found for the current user',

                        'count': 0,

                        'data': []

                    },

                    status=status.HTTP_200_OK  # Changed from 404 to 200 for better UX

                )

            

            serializer = self.get_serializer(shops, many=True)

            return Response({

                'message': f'Found {shops.count()} shop(s)',

                'count': shops.count(),

                'data': serializer.data

            }, status=status.HTTP_200_OK)

        

        except Exception as e:

            print(f"DEBUG: Exception in my_shops: {str(e)}")

            return Response(

                {'message': 'Error retrieving shops', 'error': str(e)},

                status=status.HTTP_500_INTERNAL_SERVER_ERROR

            )



    @action(detail=False, methods=['get'])
    def nearby(self, request):

        """Get shops within a specified radius of a location."""

        lat = request.query_params.get('lat')

        lng = request.query_params.get('lng')

        radius = request.query_params.get('radius', 5)  # Default 5km

        verified_only = request.query_params.get('verified_only', 'false').lower() == 'true'

        active_only = request.query_params.get('active_only', 'true').lower() == 'true'



        if not lat or not lng:

            return Response(

                {'message': 'Latitude and longitude are required'},

                status=status.HTTP_400_BAD_REQUEST

            )



        try:

            user_location = Point(float(lng), float(lat), srid=4326)

            radius_km = float(radius)

            

            # Build the query

            nearby_shops = Shop.objects.filter(

                location__distance_lte=(user_location, D(km=radius_km))

            ).exclude(

                location__isnull=True

            ).annotate(

                distance=Distance('location', user_location)

            )

            

            # Apply filters

            if active_only:

                nearby_shops = nearby_shops.filter(is_active=True)

            if verified_only:

                nearby_shops = nearby_shops.filter(is_verified=True)

                

            nearby_shops = nearby_shops.order_by('distance')



            serializer = self.get_serializer(nearby_shops, many=True)

            

            # Add distance to each shop in the response

            for i, shop_data in enumerate(serializer.data):

                if i < len(nearby_shops):

                    # Convert distance from meters to kilometers

                    distance_km = nearby_shops[i].distance.km if nearby_shops[i].distance else 0

                    shop_data['distance'] = round(distance_km, 2)

            

            return Response({

                'message': f'Found {nearby_shops.count()} shops within {radius_km}km',

                'data': serializer.data,

                'count': nearby_shops.count()

            })

            

        except ValueError as e:

            return Response(

                {'message': 'Invalid coordinates or radius', 'error': str(e)},

                status=status.HTTP_400_BAD_REQUEST

            )

        except Exception as e:

            return Response(

                {'message': 'Error searching nearby shops', 'error': str(e)},

                status=status.HTTP_500_INTERNAL_SERVER_ERROR

            )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get statistics for a specific shop - FIXED VERSION."""
        try:
            shop = self.get_object()
            
            # Check permissions - only shop owner or staff can view statistics
            if not request.user.is_staff and shop.owner != request.user:
                return Response(
                    {'message': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Get all products for this shop
            products = Product.objects.filter(shop=shop)
            
            # Get all orders for products in this shop
            orders = Order.objects.filter(variant__product__shop=shop)
            
            # Get all reviews for products in this shop
            reviews = Review.objects.filter(product__shop=shop)
            
            # Basic counts
            total_products = products.count()
            total_orders = orders.count()
            
            # Revenue calculation - handle both Order model structures
            try:
                # Try the newer structure first
                total_revenue = orders.aggregate(
                    total=Sum('total_price')
                )['total'] or 0
            except:
                # Fallback to older structure
                total_revenue = 0
                for order in orders:
                    total_revenue += order.quantity * order.unit_price
            
            # Average rating
            avg_rating = reviews.aggregate(
                avg=Avg('rating')
            )['avg'] or 0
            
            # Recent statistics (last 30 days)
            thirty_days_ago = timezone.now() - timedelta(days=30)
            
            recent_orders = orders.filter(created_at__gte=thirty_days_ago).count()
            
            try:
                recent_revenue = orders.filter(created_at__gte=thirty_days_ago).aggregate(
                    total=Sum('total_price')
                )['total'] or 0
            except:
                recent_revenue = 0
                for order in orders.filter(created_at__gte=thirty_days_ago):
                    recent_revenue += order.quantity * order.unit_price
            
            # Total reviews count
            total_reviews = reviews.count()
            
            # Build response data
            statistics_data = {
                'totalProducts': total_products,
                'totalOrders': total_orders,
                'totalRevenue': float(total_revenue),
                'avgRating': round(float(avg_rating), 1) if avg_rating else 0,
                'recentOrders': recent_orders,
                'recentRevenue': float(recent_revenue),
                'totalReviews': total_reviews
            }
            
            # Log the response for debugging
            print(f"DEBUG: Statistics for shop {shop.id}: {statistics_data}")
            
            return Response(statistics_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"DEBUG: Error in statistics endpoint: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return Response(
                {'message': 'Error loading statistics', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=False, methods=['post'])
    def create_shop(self, request):
        """Create a new shop for the current user."""
        if not request.user.is_authenticated:
            return Response(
                {'message': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    # CRITICAL FIX: Use ShopCreateSerializer instead of ShopSerializer
        serializer = ShopCreateSerializer(data=request.data)
    
        if serializer.is_valid():
        # Automatically assign the shop to the current user
            shop = serializer.save(owner=request.user)
        
        # Use ShopSerializer for the response to include all fields
            response_serializer = ShopSerializer(shop, context={'request': request})
        
            return Response(
                {
                'message': 'Shop created successfully',
                'data': response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
    
        return Response(
            {
            'message': 'Error creating shop',
            'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products for a specific shop"""
        shop = self.get_object()
        products = Product.objects.filter(shop=shop).select_related('category', 'brand')
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get statistics for a specific shop"""
        shop = self.get_object()
        products = Product.objects.filter(shop=shop)
        variants = ProductVariant.objects.filter(product__shop=shop)
        
        total_inventory_value = 0
        for variant in variants:
            total_inventory_value += variant.price * variant.quantity
        
        stats = {
            'total_products': products.count(),
            'active_products': products.filter(is_active=True).count(),
            'total_variants': variants.count(),
            'active_variants': variants.filter(is_active=True).count(),
            'total_stock': variants.aggregate(total=Sum('quantity'))['total'] or 0,
            'out_of_stock_variants': variants.filter(quantity=0).count(),
            'low_stock_variants': variants.filter(quantity__lte=10, quantity__gt=0).count(),
            'total_inventory_value': total_inventory_value,
            'average_product_price': variants.aggregate(avg=Avg('price'))['avg'] or 0,
            'categories': products.values('category__category_name').annotate(
                count=Count('id')
            ).order_by('-count')[:5],
            'brands': products.values('brand__brand_name').annotate(
                count=Count('id')
            ).order_by('-count')[:5]
        }
        
        return Response(stats)
    
    def destroy(self, request, *args, **kwargs):
        """
       Delete a shop - only owner or staff can delete
        """
        try:
            shop = self.get_object()
        
            # Check permissions - only shop owner or staff can delete
            if not request.user.is_staff and shop.owner != request.user:
                return Response(
                    {'message': 'Permission denied. You can only delete your own shops.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
            # Check if shop has products
            product_count = Product.objects.filter(shop=shop).count()
            if product_count > 0:
                return Response(
                    {
                        'message': f'Cannot delete shop. It has {product_count} associated products.',
                        'error': 'Please delete all products before deleting the shop.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
            # Check if shop has orders
            order_count = Order.objects.filter(variant__product__shop=shop).count()
            if order_count > 0:
                return Response(
                    {
                        'message': f'Cannot delete shop. It has {order_count} associated orders.',
                        'error': 'Shops with order history cannot be deleted.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
            # Delete the shop
            shop_name = shop.name
            shop.delete()
        
            return Response(
                {
                    'message': f'Shop "{shop_name}" deleted successfully',
                    'success': True
                },
                status=status.HTTP_200_OK
            )
        
        except Exception as e:
            print(f"DEBUG: Error deleting shop: {str(e)}")
            import traceback
            traceback.print_exc()
        
            return Response(
                {'message': 'Error deleting shop', 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'variant', 'rating', 'user']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Review.objects.select_related('product', 'variant', 'user')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status'] 
    ordering_fields = ['created_at', 'total_price']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
    
        # Check if filtering by shop (seller view)
        shop_id = self.request.query_params.get('variant__product__shop')
    
        if shop_id:
            # Seller viewing orders for a specific shop
            try:
                shop = Shop.objects.get(id=shop_id, owner=user)
                return Order.objects.filter(
                    variant__product__shop=shop
                ).select_related(
                    'user', 'variant__product__shop', 'variant__size', 'variant__color',
                    'variant__product', 'variant__product__brand', 'variant__product__category'
                ).prefetch_related(
                    'variant__images'
                ).order_by('-created_at')
            except Shop.DoesNotExist:
                return Order.objects.none()
    
        # No shop filter - return buyer's orders (customer view)
        return Order.objects.filter(
            user=user
        ).select_related(
            'user', 'variant__product__shop', 'variant__size', 'variant__color',
            'variant__product', 'variant__product__brand', 'variant__product__category'
        ).prefetch_related(
            'variant__images'
        ).order_by('-created_at')
        
    def list(self, request, *args, **kwargs):
        """Override list to handle pagination correctly"""
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available_for_delivery(self, request):
        """
        Orders that are confirmed/processing and do not yet have an active Delivery object.
        """
        orders_ready = Order.objects.filter(
            status__in=['confirmed', 'processing', 'shipped']
        ).select_related(
            'user', 'variant__product__shop', 'variant__size', 'variant__color',
            'variant__product'
        ).prefetch_related('variant__images')
        
        orders_with_delivery = Delivery.objects.filter(
            status__in=['accepted', 'pending', 'picked_up']
        ).values_list('order_id', flat=True)

        final_queryset = orders_ready.exclude(
            id__in=orders_with_delivery
        ).order_by('created_at')
        
        latitude = request.query_params.get('latitude')
        longitude = request.query_params.get('longitude')
        radius = request.query_params.get('radius_km', 10)

        if latitude and longitude:
            try:
                center_point = Point(float(longitude), float(latitude), srid=4326)
                
                final_queryset = final_queryset.filter(
                    variant__product__shop__location__distance_lte=(center_point, D(km=radius))
                ).annotate(
                    distance=Distance('variant__product__shop__location', center_point)
                ).order_by('distance')

            except (ValueError, TypeError):
                pass

        page = self.paginate_queryset(final_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(final_queryset, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """
        Auto-assign authenticated user when creating order
        FIX: Reduce variant quantity when order is created
        """
        order = serializer.save(user=self.request.user)
        
        # Reduce variant quantity
        variant = order.variant
        if variant.quantity >= order.quantity:
            variant.quantity -= order.quantity
            variant.save()
        else:
            # Rollback if insufficient stock
            order.delete()
            raise serializers.ValidationError({
                'quantity': f'Insufficient stock. Only {variant.quantity} items available.'
            })
    
    @action(detail=True, methods=['post'])
    def create_order(self, request, pk=None):
        """Create a new order for a specific product variant"""
        variant = self.get_object()
        quantity = request.data.get('quantity', 1)
        
        if variant.quantity < int(quantity):
            return Response(
                {'error': 'Insufficient stock for this variant'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = Order.objects.create(
            user=self.request.user,
            variant=variant,
            quantity=quantity,
            unit_price=variant.price,
            total_price=variant.price * int(quantity),
            status='pending'
        )
        
        # Reduce stock
        variant.quantity -= int(quantity)
        variant.save()
        
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['variant', 'variant__product']
    
    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related(
            'variant', 'variant__product', 'variant__size', 'variant__color'
        ).prefetch_related(
            'variant__images'  # Add this to prefetch images
        )
    
    def perform_create(self, serializer):
        
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def total(self, request):
        """Get cart total"""
        cart_items = self.get_queryset()
        total = sum(item.get_total_price() for item in cart_items)
        return Response({
            'total_items': cart_items.count(),
            'total_price': total
        })
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from cart"""
        deleted_count = self.get_queryset().delete()[0]
        return Response({
            'message': f'Removed {deleted_count} items from cart'
        })


class WishlistItemViewSet(viewsets.ModelViewSet):
    queryset = WishlistItem.objects.all()
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']
    
    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related('product')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from wishlist"""
        deleted_count = self.get_queryset().delete()[0]
        return Response({
            'message': f'Removed {deleted_count} items from wishlist'
        })

# Complete fixed DeliveryViewSet - Replace in views.py

class DeliveryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing deliveries
    Provides endpoints for deliverers to view, accept, and manage deliveries
    """
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deliverer', 'order']
    search_fields = ['order__id', 'delivery_address', 'notes']
    ordering_fields = ['created_at', 'estimated_time', 'delivery_fee']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DeliveryCreateSerializer
        return DeliverySerializer
    
    def get_queryset(self):
        """
        Filter deliveries based on user role - FIXED to avoid union() issues
        - Staff: see all deliveries
        - Deliverers: see their assigned deliveries
        - Shop owners: see deliveries for their shop orders
        """
        user = self.request.user
        
        # Staff sees everything
        if user.is_staff:
            return Delivery.objects.all().select_related(
                'order', 'order__variant__product__shop', 'deliverer', 'order__user',
                'order__variant', 'order__variant__product', 'order__variant__size', 
                'order__variant__color', 'order__variant__product__category',
                'order__variant__product__brand'
            ).prefetch_related(
                'order__variant__images'
            )
        
        # Use Q objects to combine filters without union()
        filter_conditions = Q(deliverer=user)  # Deliveries assigned to this user
        
        # Add shop owner condition
        user_shops = Shop.objects.filter(owner=user)
        if user_shops.exists():
            filter_conditions |= Q(order__variant__product__shop__in=user_shops)
        
        # Return combined queryset with proper select_related
        return Delivery.objects.filter(
            filter_conditions
        ).select_related(
            'order', 'order__variant__product__shop', 'deliverer', 'order__user',
            'order__variant', 'order__variant__product', 'order__variant__size', 
            'order__variant__color', 'order__variant__product__category',
            'order__variant__product__brand'
        ).prefetch_related(
            'order__variant__images'
        ).distinct().order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def my_deliveries(self, request):
        """
        Get deliveries assigned to the current user (as deliverer)
        ENHANCED: Better prefetching and response structure
        """
        deliveries = Delivery.objects.filter(
            deliverer=request.user
        ).select_related(
            'order',
            'order__user',
            'order__variant',
            'order__variant__product',
            'order__variant__product__shop',
            'order__variant__product__category',
            'order__variant__product__brand',
            'order__variant__size',
            'order__variant__color',
            'deliverer'
        ).prefetch_related(
            'order__variant__images'
        ).order_by('-created_at')
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter and status_filter != 'all':
            deliveries = deliveries.filter(status=status_filter)
        
        # Paginate results
        page = self.paginate_queryset(deliveries)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(deliveries, many=True)
        return Response({
            'count': deliveries.count(),
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get orders available for delivery (not yet assigned to a deliverer)
        Optionally filter by location proximity
        """
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = float(request.query_params.get('radius', 10))  # Default 10km
        
        # Get orders that need delivery but don't have a deliverer yet
        available_orders = Order.objects.filter(
            status__in=['confirmed', 'processing'],
            deliverer__isnull=True
        ).select_related(
            'variant__product__shop', 'user', 'variant__product',
            'variant__size', 'variant__color'
        )
        
        # Filter by location if coordinates provided
        if lat and lng:
            try:
                user_location = Point(float(lng), float(lat), srid=4326)
                
                # Filter shops within radius
                available_orders = available_orders.filter(
                    variant__product__shop__location__distance_lte=(user_location, D(km=radius))
                ).exclude(
                    variant__product__shop__location__isnull=True
                ).annotate(
                    distance=Distance('variant__product__shop__location', user_location)
                ).order_by('distance')
                
            except (ValueError, TypeError) as e:
                return Response(
                    {'error': 'Invalid coordinates provided'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Serialize the orders
        from .serializers import OrderSerializer
        serializer = OrderSerializer(available_orders, many=True, context={'request': request})
        
        # Add distance to response if calculated
        if lat and lng:
            for i, order_data in enumerate(serializer.data):
                if i < len(available_orders) and hasattr(available_orders[i], 'distance'):
                    order_data['distance'] = round(available_orders[i].distance.km, 2)
        
        return Response({
            'count': available_orders.count(),
            'radius_km': radius if lat and lng else None,
            'data': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def accept_order(self, request):
        """Accept an order for delivery"""
        order_id = request.data.get('order_id')
        estimated_time = request.data.get('estimated_time', 30)  # minutes
        
        if not order_id:
            return Response(
                {'error': 'order_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = Order.objects.get(id=order_id)
            
            # Check if order is available
            if order.deliverer is not None:
                return Response(
                    {'error': 'This order is already assigned to a deliverer'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if order.status not in ['confirmed', 'processing']:
                return Response(
                    {'error': f'Order status must be confirmed or processing, current status: {order.status}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Assign deliverer to order
            order.deliverer = request.user
            order.estimated_delivery_time = estimated_time
            order.save()
            
            # Create delivery record
            delivery = Delivery.objects.create(
                order=order,
                deliverer=request.user,
                pickup_address=order.variant.product.shop.address,
                delivery_address=order.delivery_address or '',
                estimated_time=estimated_time,
                delivery_fee=order.delivery_fee,
                status='accepted'
            )
            
            serializer = self.get_serializer(delivery)
            return Response({
                'message': 'Order accepted successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update delivery status - FIXED to work with Q-filtered queryset"""
        try:
            # Get delivery with explicit query to avoid union() issues
            delivery = Delivery.objects.select_related(
                'order', 'order__variant__product__shop', 'deliverer'
            ).get(pk=pk)
            
            # Check permission - deliverer or staff can update
            if delivery.deliverer != request.user and not request.user.is_staff:
                # Also check if user is shop owner
                if not Shop.objects.filter(
                    owner=request.user, 
                    products__variants__orders=delivery.order
                ).exists():
                    return Response(
                        {'error': 'You do not have permission to update this delivery'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            new_status = request.data.get('status')
            
            valid_statuses = ['accepted', 'picked_up', 'in_transit', 'delivered', 'cancelled', 'failed']
            
            if not new_status or new_status not in valid_statuses:
                return Response(
                    {'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            old_status = delivery.status
            delivery.status = new_status
            
            # Update timestamps
            if new_status == 'picked_up' and not delivery.pickup_time:
                delivery.pickup_time = timezone.now()
            elif new_status == 'delivered' and not delivery.delivery_time:
                delivery.delivery_time = timezone.now()
                # Calculate actual delivery time
                if delivery.pickup_time:
                    time_diff = delivery.delivery_time - delivery.pickup_time
                    delivery.actual_time = int(time_diff.total_seconds() / 60)
            
            delivery.save()
            
            # Update order status accordingly
            order = delivery.order
            if new_status == 'picked_up':
                order.status = 'shipped'
            elif new_status == 'delivered':
                order.status = 'delivered'
            elif new_status in ['cancelled', 'failed']:
                order.status = 'cancelled'
                order.deliverer = None
            order.save()
            
            serializer = self.get_serializer(delivery)
            return Response({
                'message': f'Delivery status updated from {old_status} to {new_status}',
                'data': serializer.data
            })
            
        except Delivery.DoesNotExist:
            return Response(
                {'error': 'Delivery not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Error updating delivery: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def mark_picked_up(self, request, pk=None):
        """Mark delivery as picked up from shop"""
        delivery = self.get_object()
        
        if delivery.deliverer != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        delivery.status = 'picked_up'
        delivery.pickup_time = timezone.now()
        delivery.save()
        
        # Update order status
        delivery.order.status = 'shipped'
        delivery.order.save()
        
        serializer = self.get_serializer(delivery)
        return Response({
            'message': 'Marked as picked up',
            'data': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def mark_delivered(self, request, pk=None):
        """Mark delivery as completed"""
        delivery = self.get_object()
        
        if delivery.deliverer != request.user and not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        delivery.status = 'delivered'
        delivery.delivery_time = timezone.now()
        
        # Calculate actual delivery time
        if delivery.pickup_time:
            time_diff = delivery.delivery_time - delivery.pickup_time
            delivery.actual_time = int(time_diff.total_seconds() / 60)
        
        delivery.save()
        
        # Update order status
        delivery.order.status = 'delivered'
        delivery.order.save()
        
        serializer = self.get_serializer(delivery)
        return Response({
            'message': 'Delivery completed successfully',
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get delivery statistics for current user"""
        deliveries = Delivery.objects.filter(deliverer=request.user)
        
        # Overall stats
        total_deliveries = deliveries.count()
        completed = deliveries.filter(status='delivered').count()
        in_progress = deliveries.filter(status__in=['accepted', 'picked_up', 'in_transit']).count()
        cancelled = deliveries.filter(status__in=['cancelled', 'failed']).count()
        
        # Earnings
        total_earnings = deliveries.filter(
            status='delivered'
        ).aggregate(total=Sum('delivery_fee'))['total'] or 0
        
        # Today's stats
        today = timezone.now().date()
        today_deliveries = deliveries.filter(created_at__date=today)
        completed_today = today_deliveries.filter(status='delivered').count()
        earnings_today = today_deliveries.filter(
            status='delivered'
        ).aggregate(total=Sum('delivery_fee'))['total'] or 0
        
        # This week's stats
        week_start = timezone.now() - timedelta(days=7)
        week_deliveries = deliveries.filter(created_at__gte=week_start)
        completed_week = week_deliveries.filter(status='delivered').count()
        earnings_week = week_deliveries.filter(
            status='delivered'
        ).aggregate(total=Sum('delivery_fee'))['total'] or 0
        
        # Average delivery time
        avg_time = deliveries.filter(
            status='delivered',
            actual_time__isnull=False
        ).aggregate(avg=Avg('actual_time'))['avg'] or 0
        
        # Success rate
        success_rate = (completed / total_deliveries * 100) if total_deliveries > 0 else 0
        
        return Response({
            'total_deliveries': total_deliveries,
            'completed_deliveries': completed,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'success_rate': round(success_rate, 1),
            'total_earnings': float(total_earnings),
            'average_delivery_time': round(float(avg_time), 1),
            'today': {
                'deliveries': today_deliveries.count(),
                'completed': completed_today,
                'earnings': float(earnings_today)
            },
            'this_week': {
                'deliveries': week_deliveries.count(),
                'completed': completed_week,
                'earnings': float(earnings_week)
            }
        })