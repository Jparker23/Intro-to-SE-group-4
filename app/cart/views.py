from django.shortcuts import render, redirect, get_object_or_404
from decimal import Decimal
from django.views.decorators.http import require_POST
from shop.models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required



@login_required
def cart_details(request):
    #should fetch a list of products in the cart from the DB and render a template to display them
    cart, _  = Cart.objects.get_or_create(buyer=request.user)
    cart_items = CartItem.objects.filter(cart=cart).select_related("product")
    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    item_count = sum(item.quantity for item in cart_items)
    tax = subtotal * Decimal("0.07") if subtotal else Decimal("0.00")
    total = subtotal + tax 
    #each prod should have a add to cart button
    return render(request, "generic/cart.html", {"cart_items": cart_items, "item_count": item_count,"subtotal": subtotal,"tax": tax, "total": total,})

@login_required
@require_POST
def add_to_cart(request, product_id): #when user clicks add to cart, this is triggered
    product = get_object_or_404(Product, id=product_id, is_approved=True) #make sure only approved prods can go to the cart
    cart, _ = Cart.objects.get_or_create(buyer=request.user)
    #add 1 quantity
    quantity = int(request.POST.get('quantity', 1))
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
        item.quantity = min(quantity, product.stock)
    else:
        item.quantity = min(item.quantity + quantity, product.stock)

    item.save()
    return redirect(request.META.get("HTTP_REFERER", "/api/catalog/")) #sends user back to the page that they came from

@login_required
def remove_from_cart(request, item_id): #removing a item from cart
    cart, _ = Cart.objects.get_or_create(buyer=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart__buyer=request.user)
    item.delete()
    return redirect("cart:cart_details") #directs user back to cart to view updated cart


@login_required
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