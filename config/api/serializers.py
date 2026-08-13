from rest_framework import serializers

from product.models import Brand, Category, Product, Review
from orders.models import Order, OrderItem


class BrandSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source='products.count', read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'product_count']


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source='products.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'product_count']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'rating', 'comment', 'created_at']


class ProductListSerializer(serializers.ModelSerializer):
    """Lighter-weight serializer for list views (browsing many products)."""
    brand = serializers.CharField(source='brand.name', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    stock_status = serializers.CharField(read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'brand', 'category', 'scale', 'material',
            'price', 'old_price', 'stock', 'stock_status', 'tag',
            'average_rating', 'review_count', 'image_url',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full serializer for a single product, including specs and reviews."""
    brand = serializers.CharField(source='brand.name', read_only=True)
    category = serializers.CharField(source='category.name', read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    stock_status = serializers.CharField(read_only=True)
    feature_list = serializers.ListField(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'brand', 'category', 'scale', 'material',
            'color', 'dimensions', 'manufacturer', 'release_year', 'recommended_age',
            'description', 'feature_list', 'price', 'old_price', 'stock', 'stock_status',
            'tag', 'average_rating', 'review_count', 'reviews', 'image_url', 'sku',
        ]

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None


class OrderItemSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_name', 'brand_name', 'unit_price', 'quantity', 'line_total']


class OrderTrackSerializer(serializers.ModelSerializer):
    """Deliberately excludes personal info (address, phone, email) — this
    endpoint is public-by-order-number, same as the site's Track Order page."""
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'order_number', 'status', 'status_display', 'payment_method_display',
            'subtotal', 'shipping_cost', 'tax', 'total',
            'estimated_delivery', 'created_at', 'items',
        ]