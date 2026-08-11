from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Product, Category, Brand, Review, Wishlist


def home(request):from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Product, Category, Brand, Review, Wishlist


def home(request):
    trending = Product.objects.filter(is_active=True, tag__in=['best', 'new']).select_related('brand', 'category')[:4]
    featured = Product.objects.filter(is_active=True).select_related('brand', 'category').order_by('-created_at')[4:8]
    sale_items = Product.objects.filter(is_active=True, tag='sale')[:4]
    categories = Category.objects.all()
    brands = Brand.objects.filter(is_featured=True)
    reviews = Review.objects.select_related('product').order_by('-rating', '-created_at')[:3]

    # Prefer a product with a real uploaded photo for the hero banner,
    # regardless of its tag — falls back to trending, then any active product.
    hero_product = None
    for p in Product.objects.filter(is_active=True).order_by('-created_at'):
        if p.image:
            hero_product = p
            break
    if not hero_product:
        hero_product = trending.first() or Product.objects.filter(is_active=True).first()
    product_count = Product.objects.filter(is_active=True).count()

    return render(request, 'website/index.html', {
        'trending': trending,
        'featured': featured,
        'sale_items': sale_items,
        'categories': categories,
        'brands': brands,
        'reviews': reviews,
        'hero_product': hero_product,
        'product_count': product_count,
    })


def about(request):
    return render(request, 'website/about.html')


def contact(request):
    from pages.models import ContactMessage
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name', ''),
            email=request.POST.get('email', ''),
            subject=request.POST.get('subject', ''),
            message=request.POST.get('message', ''),
        )
        messages.success(request, "Thanks for reaching out — our team will get back to you within 24 hours.")
        return redirect('contact')
    return render(request, 'website/contact.html')


def help_center(request):
    return render(request, 'website/help.html')


def shop(request):
    products = Product.objects.filter(is_active=True).select_related('brand', 'category')

    q = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    brand_slug = request.GET.get('brand', '')
    scale = request.GET.get('scale', '')
    price_range = request.GET.get('price', '')
    sort = request.GET.get('sort', 'trending')
    in_stock_only = request.GET.get('in_stock', '')

    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(brand__name__icontains=q) | Q(category__name__icontains=q)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    if scale:
        products = products.filter(scale=scale)
    if price_range:
        try:
            lo, hi = price_range.split('-')
            products = products.filter(price__gte=float(lo), price__lte=float(hi))
        except ValueError:
            pass
    if in_stock_only:
        products = products.filter(stock__gt=0)

    if sort == 'priceLow':
        products = products.order_by('price')
    elif sort == 'priceHigh':
        products = products.order_by('-price')
    elif sort == 'new':
        products = products.filter(tag='new')
    elif sort == 'best':
        products = products.filter(tag='best')
    elif sort == 'sale':
        products = products.filter(tag='sale')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'scale_choices': Product.SCALE_CHOICES,
        'total_count': products.count(),
        'current': {
            'q': q, 'category': category_slug, 'brand': brand_slug,
            'scale': scale, 'price': price_range, 'sort': sort, 'in_stock': in_stock_only,
        },
    }
    return render(request, 'website/shop.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('brand', 'category'), slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    if related.count() < 4:
        extra = Product.objects.filter(is_active=True).exclude(pk=product.pk).exclude(
            pk__in=related.values_list('pk', flat=True))[:4 - related.count()]
        related = list(related) + list(extra)

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    if request.method == 'POST' and request.POST.get('form_type') == 'review':
        if not request.user.is_authenticated:
            messages.error(request, "Please sign in to leave a review.")
            return redirect('login')
        Review.objects.create(
            product=product,
            user=request.user,
            name=request.user.get_full_name() or request.user.username,
            rating=int(request.POST.get('rating', 5)),
            comment=request.POST.get('comment', ''),
        )
        messages.success(request, "Thanks — your review has been posted.")
        return redirect('product_detail', slug=slug)

    return render(request, 'website/product_detail.html', {
        'product': product,
        'related': related,
        'in_wishlist': in_wishlist,
        'reviews': product.reviews.all()[:20],
    })


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__brand')
    return render(request, 'website/wishlist.html', {'items': items})


@login_required
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        messages.info(request, f'Removed {product.name} from your wishlist.')
    else:
        messages.success(request, f'Added {product.name} to your wishlist.')
    next_url = request.POST.get('next') or request.GET.get('next') or 'shop'
    return redirect(next_url)
    trending = Product.objects.filter(is_active=True, tag__in=['best', 'new']).select_related('brand', 'category')[:4]
    featured = Product.objects.filter(is_active=True).select_related('brand', 'category').order_by('-created_at')[4:8]
    sale_items = Product.objects.filter(is_active=True, tag='sale')[:4]
    categories = Category.objects.all()
    brands = Brand.objects.filter(is_featured=True)
    reviews = Review.objects.select_related('product').order_by('-rating', '-created_at')[:3]
    hero_product = trending.first() or Product.objects.filter(is_active=True).first()
    product_count = Product.objects.filter(is_active=True).count()

    return render(request, 'website/index.html', {
        'trending': trending,
        'featured': featured,
        'sale_items': sale_items,
        'categories': categories,
        'brands': brands,
        'reviews': reviews,
        'hero_product': hero_product,
        'product_count': product_count,
    })


def about(request):
    return render(request, 'website/about.html')


def contact(request):
    from pages.models import ContactMessage
    if request.method == 'POST':
        ContactMessage.objects.create(
            name=request.POST.get('name', ''),
            email=request.POST.get('email', ''),
            subject=request.POST.get('subject', ''),
            message=request.POST.get('message', ''),
        )
        messages.success(request, "Thanks for reaching out — our team will get back to you within 24 hours.")
        return redirect('contact')
    return render(request, 'website/contact.html')


def help_center(request):
    return render(request, 'website/help.html')


def shop(request):
    products = Product.objects.filter(is_active=True).select_related('brand', 'category')

    q = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')
    brand_slug = request.GET.get('brand', '')
    scale = request.GET.get('scale', '')
    price_range = request.GET.get('price', '')
    sort = request.GET.get('sort', 'trending')
    in_stock_only = request.GET.get('in_stock', '')

    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(brand__name__icontains=q) | Q(category__name__icontains=q)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)
    if scale:
        products = products.filter(scale=scale)
    if price_range:
        try:
            lo, hi = price_range.split('-')
            products = products.filter(price__gte=float(lo), price__lte=float(hi))
        except ValueError:
            pass
    if in_stock_only:
        products = products.filter(stock__gt=0)

    if sort == 'priceLow':
        products = products.order_by('price')
    elif sort == 'priceHigh':
        products = products.order_by('-price')
    elif sort == 'new':
        products = products.filter(tag='new')
    elif sort == 'best':
        products = products.filter(tag='best')
    elif sort == 'sale':
        products = products.filter(tag='sale')
    else:
        products = products.order_by('-created_at')

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'scale_choices': Product.SCALE_CHOICES,
        'total_count': products.count(),
        'current': {
            'q': q, 'category': category_slug, 'brand': brand_slug,
            'scale': scale, 'price': price_range, 'sort': sort, 'in_stock': in_stock_only,
        },
    }
    return render(request, 'website/shop.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('brand', 'category'), slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    if related.count() < 4:
        extra = Product.objects.filter(is_active=True).exclude(pk=product.pk).exclude(
            pk__in=related.values_list('pk', flat=True))[:4 - related.count()]
        related = list(related) + list(extra)

    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    if request.method == 'POST' and request.POST.get('form_type') == 'review':
        if not request.user.is_authenticated:
            messages.error(request, "Please sign in to leave a review.")
            return redirect('login')
        Review.objects.create(
            product=product,
            user=request.user,
            name=request.user.get_full_name() or request.user.username,
            rating=int(request.POST.get('rating', 5)),
            comment=request.POST.get('comment', ''),
        )
        messages.success(request, "Thanks — your review has been posted.")
        return redirect('product_detail', slug=slug)

    return render(request, 'website/product_detail.html', {
        'product': product,
        'related': related,
        'in_wishlist': in_wishlist,
        'reviews': product.reviews.all()[:20],
    })


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__brand')
    return render(request, 'website/wishlist.html', {'items': items})


@login_required
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        obj.delete()
        messages.info(request, f'Removed {product.name} from your wishlist.')
    else:
        messages.success(request, f'Added {product.name} to your wishlist.')
    next_url = request.POST.get('next') or request.GET.get('next') or 'shop'
    return redirect(next_url)
