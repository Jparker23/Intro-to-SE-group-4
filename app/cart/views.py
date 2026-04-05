from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.views.decorators.http import require_POST
from shop.models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

def buyer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != "buyer":
            return redirect("home")
        return view_func(request, *args, **kwargs)
    return wrapper


@never_cache
@login_required
@buyer_required
def cart_details(request):
    cart, _ = Cart.objects.get_or_create(buyer=request.user)
    cart_items = CartItem.objects.filter(cart=cart).select_related("product")
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    item_count = sum(item.quantity for item in cart_items)
    tax = subtotal * Decimal("0.10") if subtotal else Decimal("0.00")
    total = subtotal + tax

    return render(
        request,
        "generic/cart.html",
        {
            "cart_items": cart_items,
            "item_count": item_count,
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
        },
    )


@never_cache
@login_required
@buyer_required
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_approved=True)
    cart, _ = Cart.objects.get_or_create(buyer=request.user)

    quantity = int(request.POST.get("quantity", 1))
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        item.quantity = min(quantity, product.stock)
    else:
        item.quantity = min(item.quantity + quantity, product.stock)

    item.save()
    return redirect(request.META.get("HTTP_REFERER", "/api/catalog/"))


@never_cache
@login_required
@buyer_required
@require_POST
def remove_from_cart(request, item_id):
    cart, _ = Cart.objects.get_or_create(buyer=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect("cart:cart_details")

@never_cache
@login_required
@buyer_required
@require_POST
def update_cart_item(request, product_id):
    cart, _ = Cart.objects.get_or_create(buyer=request.user)
    item = get_object_or_404(CartItem, cart=cart, product_id=product_id)

    quantity = int(request.POST.get("quantity", 1))

    if quantity <= 0:
        item.delete()
    else:
        item.quantity = min(quantity, item.product.stock)
        item.save()

    return redirect("cart:cart_details")