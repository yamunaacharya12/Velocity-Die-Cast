"""
URL configuration for the Velocity Die-Cast store.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from product import views as product_views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", product_views.home, name="home"),
    path("about/", product_views.about, name="about"),
    path("contact/", product_views.contact, name="contact"),
    path("help/", product_views.help_center, name="help"),
    path("shop/", product_views.shop, name="shop"),
    path("wishlist/", product_views.wishlist_view, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", product_views.wishlist_toggle, name="wishlist_toggle"),

    path("cart/", include("cart.urls")),
    path("", include("orders.urls")),
    path("", include("accounts.urls")),
    path("", include("pages.urls")),

    path("product/", include("product.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
