from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/confirmation/<str:order_number>/', views.order_confirmation, name='order_confirmation'),
    path('account/orders/', views.order_history, name='order_history'),
    path('track-order/', views.track_order, name='track_order'),
]
