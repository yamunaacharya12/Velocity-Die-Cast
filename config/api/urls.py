from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('products', views.ProductViewSet, basename='api-product')
router.register('categories', views.CategoryViewSet, basename='api-category')
router.register('brands', views.BrandViewSet, basename='api-brand')

urlpatterns = [
    path('', include(router.urls)),
    path('products/<slug:slug>/reviews/', views.ProductReviewsView.as_view(), name='api-product-reviews'),
    path('orders/<str:order_number>/track/', views.track_order_api, name='api-order-track'),
]