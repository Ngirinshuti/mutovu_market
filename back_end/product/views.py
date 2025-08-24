"""
Django REST Framework ViewSets for product management.

This module contains ViewSets for handling CRUD operations on
product-related models including Product, Size, Color, Category,
Brand, Review, Order, CartItem, and WishlistItem.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.pagination import PageNumberPagination

from product.models import (
    Product, Size, Color, Category, Brand,
    Review, Order, CartItem, WishlistItem
)
from product.serializers import (
    ProductSerializer, SizeSerializer, ColorSerializer,
    CategorySerializer, BrandSerializer, ReviewSerializer,
    OrderSerializer, CartItemSerializer, WishlistItemSerializer
)


class CustomPagination(PageNumberPagination):
    """Custom pagination class with max 10 items per page."""
    
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 10


class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Product instances."""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        """Allow anyone to view products, require auth for modifications."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """List all products with optional filtering and pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Optional filtering by category, brand, etc.
        category = request.query_params.get('category', None)
        brand = request.query_params.get('brand', None)
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        search = request.query_params.get('search', None)
        
        
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if brand:
            queryset = queryset.filter(brand__name__icontains=brand)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # Fallback if pagination is disabled
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Products retrieved successfully',
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Create a new product."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                {
                    'message': 'Product created successfully',
                    'data': ProductSerializer(product).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Error creating product',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """Update an existing product."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        if serializer.is_valid():
            product = serializer.save()
            return Response(
                {
                    'message': 'Product updated successfully',
                    'data': ProductSerializer(product).data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Error updating product',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a product."""
        try:
            instance = self.get_object()
            product_name = instance.name
            instance.delete()
            return Response(
                {
                    'message': f'Product "{product_name}" deleted successfully'
                },
                status=status.HTTP_200_OK
            )
        except Product.DoesNotExist:
            return Response(
                {
                    'message': 'Product not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {
                    'message': 'Error deleting product',
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class SizeViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Size instances."""

    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        """Allow anyone to view sizes, require auth for modifications."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """List all sizes with pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Sizes retrieved successfully',
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Create a new size."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            size = serializer.save()
            return Response(
                {
                    'message': 'Size created successfully',
                    'data': SizeSerializer(size).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Error creating size',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """Update an existing size."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        if serializer.is_valid():
            size = serializer.save()
            return Response(
                {
                    'message': 'Size updated successfully',
                    'data': SizeSerializer(size).data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Error updating size',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a size."""
        try:
            instance = self.get_object()
            size_name = instance.name
            instance.delete()
            return Response(
                {
                    'message': f'Size "{size_name}" deleted successfully'
                },
                status=status.HTTP_200_OK
            )
        except Size.DoesNotExist:
            return Response(
                {
                    'message': 'Size not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {
                    'message': 'Error deleting size',
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ColorViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Color instances."""

    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        """Allow anyone to view colors, require auth for modifications."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """List all colors with pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Colors retrieved successfully',
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Create a new color."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            color = serializer.save()
            return Response(
                {
                    'message': 'Color created successfully',
                    'data': ColorSerializer(color).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Error creating color',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """Update an existing color."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        if serializer.is_valid():
            color = serializer.save()
            return Response(
                {
                    'message': 'Color updated successfully',
                    'data': ColorSerializer(color).data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Error updating color',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a color."""
        try:
            instance = self.get_object()
            color_name = instance.name
            instance.delete()
            return Response(
                {
                    'message': f'Color "{color_name}" deleted successfully'
                },
                status=status.HTTP_200_OK
            )
        except Color.DoesNotExist:
            return Response(
                {
                    'message': 'Color not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {
                    'message': 'Error deleting color',
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Category instances."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        """Allow anyone to view categories, require auth for modifications."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """List all categories with pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Categories retrieved successfully',
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Create a new category."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response(
                {
                    'message': 'Category created successfully',
                    'data': CategorySerializer(category).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Error creating category',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """Update an existing category."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        if serializer.is_valid():
            category = serializer.save()
            return Response(
                {
                    'message': 'Category updated successfully',
                    'data': CategorySerializer(category).data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Error updating category',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a category."""
        try:
            instance = self.get_object()
            category_name = instance.name
            instance.delete()
            return Response(
                {
                    'message': f'Category "{category_name}" deleted successfully'
                },
                status=status.HTTP_200_OK
            )
        except Category.DoesNotExist:
            return Response(
                {
                    'message': 'Category not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {
                    'message': 'Error deleting category',
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class BrandViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Brand instances."""

    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        """Allow anyone to view brands, require auth for modifications."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """List all brands with pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Brands retrieved successfully',
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Create a new brand."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            brand = serializer.save()
            return Response(
                {
                    'message': 'Brand created successfully',
                    'data': BrandSerializer(brand).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Error creating brand',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """Update an existing brand."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        if serializer.is_valid():
            brand = serializer.save()
            return Response(
                {
                    'message': 'Brand updated successfully',
                    'data': BrandSerializer(brand).data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Error updating brand',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a brand."""
        try:
            instance = self.get_object()
            brand_name = instance.name
            instance.delete()
            return Response(
                {
                    'message': f'Brand "{brand_name}" deleted successfully'
                },
                status=status.HTTP_200_OK
            )
        except Brand.DoesNotExist:
            return Response(
                {
                    'message': 'Brand not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {
                    'message': 'Error deleting brand',
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Review instances."""

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        """Allow anyone to view reviews, require auth for modifications."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        """List reviews with optional product filtering and pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Optional filtering by product
        product_id = request.query_params.get('product', None)
        rating = request.query_params.get('rating', None)
        
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if rating:
            queryset = queryset.filter(rating=rating)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Reviews retrieved successfully',
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Create a new review."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Automatically assign the review to the current user
            review = serializer.save(user=request.user)
            return Response(
                {
                    'message': 'Review created successfully',
                    'data': ReviewSerializer(review).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Error creating review',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """Update an existing review (only by the review owner)."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check if the user owns this review
        if instance.user != request.user:
            return Response(
                {
                    'message': 'You can only update your own reviews'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        if serializer.is_valid():
            review = serializer.save()
            return Response(
                {
                    'message': 'Review updated successfully',
                    'data': ReviewSerializer(review).data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Error updating review',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a review (only by the review owner)."""
        try:
            instance = self.get_object()

            # Check if the user owns this review
            if instance.user != request.user:
                return Response(
                    {
                        'message': 'You can only delete your own reviews'
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            instance.delete()
            return Response(
                {
                    'message': 'Review deleted successfully'
                },
                status=status.HTTP_200_OK
            )
        except Review.DoesNotExist:
            return Response(
                {
                    'message': 'Review not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {
                    'message': 'Error deleting review',
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Order instances."""

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """Filter orders to only show user's own orders."""
        return Order.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """List user's orders with optional status filtering and pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Optional filtering by status
        status_filter = request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Order by creation date (newest first)
        queryset = queryset.order_by('-created_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Orders retrieved successfully',
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Create a new order."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Automatically assign the order to the current user
            order = serializer.save(user=request.user)
            return Response(
                {
                    'message': 'Order created successfully',
                    'data': OrderSerializer(order).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Error creating order',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """Update an existing order (limited updates allowed)."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Restrict which fields can be updated based on order status
        if hasattr(instance, 'status') and instance.status in ['shipped', 'delivered']:
            return Response(
                {
                    'message': 'Cannot update order that has been shipped or delivered'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        if serializer.is_valid():
            order = serializer.save()
            return Response(
                {
                    'message': 'Order updated successfully',
                    'data': OrderSerializer(order).data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Error updating order',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Cancel/Delete an order (only if not processed)."""
        try:
            instance = self.get_object()

            # Only allow deletion if order hasn't been processed
            if hasattr(instance, 'status') and instance.status not in ['pending', 'confirmed']:
                return Response(
                    {
                        'message': 'Cannot cancel order that is being processed or completed'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            order_id = instance.id
            instance.delete()
            return Response(
                {
                    'message': f'Order #{order_id} cancelled successfully'
                },
                status=status.HTTP_200_OK
            )
        except Order.DoesNotExist:
            return Response(
                {
                    'message': 'Order not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {
                    'message': 'Error cancelling order',
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class CartItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing CartItem instances."""

    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """Filter cart items to only show user's own items."""
        return CartItem.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """List user's cart items with pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Calculate total cart value for all items (not just current page)
        all_items = self.get_queryset()
        total_value = sum(
            item.quantity * item.product.price for item in all_items
            if item.product and hasattr(item.product, 'price')
        )
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Add total_value to paginated response
            response = self.get_paginated_response(serializer.data)
            response.data['total_value'] = total_value
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Cart items retrieved successfully',
            'count': queryset.count(),
            'total_value': total_value,
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Add item to cart."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check if item already exists in cart
            product_id = request.data.get('product')
            existing_item = CartItem.objects.filter(
                user=request.user, product_id=product_id
            ).first()

            if existing_item:
                # Update quantity instead of creating new item
                existing_item.quantity += int(request.data.get('quantity', 1))
                existing_item.save()
                return Response(
                    {
                        'message': 'Cart item quantity updated',
                        'data': CartItemSerializer(existing_item).data
                    },
                    status=status.HTTP_200_OK
                )

            cart_item = serializer.save(user=request.user)
            return Response(
                {
                    'message': 'Item added to cart successfully',
                    'data': CartItemSerializer(cart_item).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Error adding item to cart',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """Update cart item (typically quantity)."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        if serializer.is_valid():
            cart_item = serializer.save()
            return Response(
                {
                    'message': 'Cart item updated successfully',
                    'data': CartItemSerializer(cart_item).data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Error updating cart item',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Remove item from cart."""
        try:
            instance = self.get_object()
            product_name = instance.product.name if instance.product else "Unknown"
            instance.delete()
            return Response(
                {
                    'message': f'"{product_name}" removed from cart successfully'
                },
                status=status.HTTP_200_OK
            )
        except CartItem.DoesNotExist:
            return Response(
                {
                    'message': 'Cart item not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {
                    'message': 'Error removing item from cart',
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class WishlistItemViewSet(viewsets.ModelViewSet):
    """ViewSet for managing WishlistItem instances."""

    queryset = WishlistItem.objects.all()
    serializer_class = WishlistItemSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """Filter wishlist items to only show user's own items."""
        return WishlistItem.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """List user's wishlist items with pagination."""
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'message': 'Wishlist items retrieved successfully',
            'count': queryset.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)


    def create(self, request, *args, **kwargs):
        """Add item to wishlist."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check if item already exists in wishlist
            product_id = request.data.get('product')
            existing_item = WishlistItem.objects.filter(
                user=request.user, product_id=product_id
            ).first()

            if existing_item:
                return Response(
                    {
                        'message': 'Item already in wishlist',
                        'data': WishlistItemSerializer(existing_item).data
                    },
                    status=status.HTTP_200_OK
                )

            wishlist_item = serializer.save(user=request.user)
            return Response(
                {
                    'message': 'Item added to wishlist successfully',
                    'data': WishlistItemSerializer(wishlist_item).data
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                'message': 'Error adding item to wishlist',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """Update wishlist item."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        if serializer.is_valid():
            wishlist_item = serializer.save()
            return Response(
                {
                    'message': 'Wishlist item updated successfully',
                    'data': WishlistItemSerializer(wishlist_item).data
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                'message': 'Error updating wishlist item',
                'errors': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """Remove item from wishlist."""
        try:
            instance = self.get_object()
            product_name = instance.product.name if instance.product else "Unknown"
            instance.delete()
            return Response(
                {
                    'message': f'"{product_name}" removed from wishlist successfully'
                },
                status=status.HTTP_200_OK
            )
        except WishlistItem.DoesNotExist:
            return Response(
                {
                    'message': 'Wishlist item not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {
                    'message': 'Error removing item from wishlist',
                    'error': str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )