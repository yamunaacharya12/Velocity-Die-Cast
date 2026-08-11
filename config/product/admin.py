from django import forms
from django.contrib import admin
from .models import Brand, Category, Product, ProductImage, Review, Wishlist

admin.site.site_header = "Velocity Die-Cast Admin"
admin.site.site_title = "Velocity Admin"
admin.site.index_title = "Store Management"


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'scale', 'price', 'stock', 'tag', 'is_active')
    list_filter = ('brand', 'category', 'scale', 'tag', 'is_active', 'car_type')
    list_editable = ('price', 'stock', 'tag', 'is_active')
    search_fields = ('name', 'brand__name', 'category__name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ReviewInline]
    fieldsets = (
        ('Identity', {'fields': ('name', 'slug', 'brand', 'category', 'image')}),
        ('Specifications', {'fields': (
            'scale', 'material', 'color', 'dimensions', 'manufacturer',
            'release_year', 'recommended_age',
        )}),
        ('Placeholder Illustration', {'fields': ('car_type', 'accent_color', 'has_spoiler'),
            'description': 'Used to render an on-brand illustration when no photo is uploaded.'}),
        ('Content', {'fields': ('description', 'features')}),
        ('Commerce', {'fields': ('price', 'old_price', 'stock', 'tag', 'is_active')}),
    )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('product__name', 'name', 'comment')
    formfield_overrides = {
        Review._meta.get_field('comment').__class__: {
            'widget': forms.Textarea(attrs={'rows': 8, 'cols': 70}),
        },
    }


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')