from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound

from product.models import Brand, Category, Product, Review
from orders.models import Order
from .serializers import (
    BrandSerializer, CategorySerializer, ProductListSerializer,
    ProductDetailSerializer, ReviewSerializer, OrderTrackSerializer,
)


class BrandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Browse all brands.
    GET /api/brands/         -> list every brand
    GET /api/brands/<id>/    -> a single brand
    """
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Browse all categories.
    GET /api/categories/         -> list every category
    GET /api/categories/<id>/    -> a single category
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Browse the product catalog.
    GET /api/products/                        -> list all active products
    GET /api/products/<slug>/                 -> full detail for one product
    GET /api/products/?category=<slug>        -> filter by category
    GET /api/products/?brand=<slug>            -> filter by brand
    GET /api/products/?tag=new|best|limited|sale
    GET /api/products/?search=<text>           -> search by name
    """
    queryset = Product.objects.filter(is_active=True).select_related('brand', 'category')
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductListSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.query_params
        if params.get('category'):
            qs = qs.filter(category__slug=params['category'])
        if params.get('brand'):
            qs = qs.filter(brand__slug=params['brand'])
        if params.get('tag'):
            qs = qs.filter(tag=params['tag'])
        if params.get('search'):
            qs = qs.filter(name__icontains=params['search'])
        return qs


class ProductReviewsView(generics.ListAPIView):
    """
    GET /api/products/<slug>/reviews/ -> all reviews for one product
    """
    serializer_class = ReviewSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        if not Product.objects.filter(slug=slug).exists():
            raise NotFound('No product found with that slug.')
        return Review.objects.filter(product__slug=slug)


@api_view(['GET'])
def track_order_api(request, order_number):
    """
    GET /api/orders/<order_number>/track/

    Public order lookup by order number only (no login required) — matches
    the same access level as the site's own Track Order page. Deliberately
    excludes personal info like address/phone/email.
    """
    try:
        order = Order.objects.get(order_number__iexact=order_number)
    except Order.DoesNotExist:
        raise NotFound(f'No order found with number "{order_number}".')
    serializer = OrderTrackSerializer(order)
    return Response(serializer.data)