from django.urls import path
from . import views

urlpatterns = [
    path('faq/', views.faq, name='faq'),
    path('shipping-information/', views.shipping_info, name='shipping_info'),
    path('return-refund-policy/', views.returns_policy, name='returns_policy'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms, name='terms'),
    path('blog/', views.blog_list, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
]
