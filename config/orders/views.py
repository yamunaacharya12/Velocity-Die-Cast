from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from product.models import Product
from .models import Order, OrderItem

CART_SESSION_KEY = 'cart'


def _get_cart(request):
    return request.session.setdefault(CART_SESSION_KEY, {})


def _cart_items_and_totals(request):
    cart = _get_cart(request)
    items = []
    subtotal = Decimal('0')
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            continue
        line_total = product.price * quantity
        subtotal += line_total
        items.append({'product': product, 'quantity': quantity, 'total': line_total})

    shipping = Decimal('0') if subtotal == 0 or subtotal >= Decimal(str(settings.FREE_SHIPPING_THRESHOLD)) \
        else Decimal(str(settings.STANDARD_SHIPPING_COST))
    tax = (subtotal * Decimal(str(settings.TAX_RATE))).quantize(Decimal('0.01'))
    total = subtotal + shipping + tax
    return items, subtotal, shipping, tax, total


def checkout_view(request):
    items, subtotal, shipping, tax, total = _cart_items_and_totals(request)

    if not items:
        messages.info(request, 'Your cart is empty — add a few models before checking out.')
        return redirect('cart')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()
        zip_code = request.POST.get('zip_code', '').strip()
        country = request.POST.get('country', 'Nepal').strip()
        payment_method = request.POST.get('payment_method', 'cod')

        if not (full_name and email and phone and address and city):
            messages.error(request, 'Please fill in all required fields before placing your order.')
            return render(request, 'website/checkout.html', {
                'cart_items': items, 'subtotal': subtotal, 'shipping': shipping,
                'tax': tax, 'total': total, 'payment_choices': Order.PAYMENT_CHOICES,
            })

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name, email=email, phone=phone,
            address=address, city=city, state=state, zip_code=zip_code, country=country,
            subtotal=subtotal, shipping_cost=shipping, tax=tax, total=total,
            payment_method=payment_method,
        )
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['product'].name,
                brand_name=item['product'].brand.name,
                unit_price=item['product'].price,
                quantity=item['quantity'],
            )
            # Decrement stock
            product = item['product']
            product.stock = max(0, product.stock - item['quantity'])
            product.save(update_fields=['stock'])

        request.session[CART_SESSION_KEY] = {}
        request.session.modified = True

        return redirect('order_confirmation', order_number=order.order_number)

    return render(request, 'website/checkout.html', {
        'cart_items': items, 'subtotal': subtotal, 'shipping': shipping,
        'tax': tax, 'total': total, 'payment_choices': Order.PAYMENT_CHOICES,
    })


def order_confirmation(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'website/order_confirmation.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'website/order_history.html', {'orders': orders})


def track_order(request):
    order = None
    searched = False
    if request.method == 'POST':
        searched = True
        number = request.POST.get('order_number', '').strip()
        order = Order.objects.filter(order_number__iexact=number).first()
        if not order:
            messages.error(request, f'No order found matching "{number}".')
    return render(request, 'website/track_order.html', {'order': order, 'searched': searched})
