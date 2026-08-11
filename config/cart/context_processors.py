def cart_count(request):
    cart = request.session.get('cart', {})
    return {'cart_count': sum(cart.values())}


def wishlisted_ids(request):
    if request.user.is_authenticated:
        ids = set(request.user.wishlist_items.values_list('product_id', flat=True))
    else:
        ids = set()
    return {'wishlisted_ids': ids}
