from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from product.models import Product

CART_SESSION_KEY = "cart"


def _get_cart(request):
    return request.session.setdefault(CART_SESSION_KEY, {})


def cart_view(request):
    cart = _get_cart(request)
    cart_items = []
    subtotal = Decimal('0')

    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            continue
        total = product.price * quantity
        subtotal += total
        cart_items.append({"product": product, "quantity": quantity, "total": total})

    shipping = Decimal('0') if subtotal == 0 or subtotal >= Decimal(str(settings.FREE_SHIPPING_THRESHOLD)) \
        else Decimal(str(settings.STANDARD_SHIPPING_COST))
    tax = (subtotal * Decimal(str(settings.TAX_RATE))).quantize(Decimal('0.01'))
    total_due = subtotal + shipping + tax

    return render(request, "website/cart.html", {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "tax": tax,
        "total_due": total_due,
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)
    key = str(product_id)
    qty = int(request.POST.get("quantity", 1)) if request.method == "POST" else 1
    cart[key] = cart.get(key, 0) + max(1, qty)
    request.session.modified = True
    messages.success(request, f"{product.name} added to cart.")

    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect("cart")


def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)
    qty = int(request.POST.get("quantity", 1)) if request.method == "POST" else 1
    cart[str(product_id)] = qty
    request.session.modified = True
    return redirect("checkout")


def update_cart(request, product_id):
    if request.method == "POST":
        cart = _get_cart(request)
        qty = int(request.POST.get("quantity", 1))
        if qty <= 0:
            cart.pop(str(product_id), None)
        else:
            cart[str(product_id)] = qty
        request.session.modified = True
    return redirect("cart")


def remove_from_cart(request, product_id):
    cart = _get_cart(request)
    cart.pop(str(product_id), None)
    request.session.modified = True
    messages.info(request, "Item removed from cart.")
    return redirect("cart")


def cart_item_count(request):
    cart = request.session.get(CART_SESSION_KEY, {})
    return sum(cart.values())
