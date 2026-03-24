from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from decimal import Decimal
from .models import Product, Address, Order, OrderItem, Payment, SavedPaymentMethod
from .forms import ProductForm
from cart.views import Cart, CartItem


#this page is pretty much all render requests to load my HTML templates and returns a HttpResponse


def home(request):
    #4 approved and in stock products on the home page
    featured_products = Product.objects.filter(is_active=True, is_approved=True)[:4]
    return render(request, "generic/home.html", {"featured_products": featured_products})

def brandResults(request, brand):
    return render(request, "generic/brandResults.html", {"brand": brand})

def catalog(request):
    return render(request, "generic/catalog.html")

#this is a catalog ONLY for buyers
def buyer_only_catalog(request):
    query = request.GET.get("query", "").strip() #product name get from search bar
    brand = request.GET.get("seller", "").strip()
    category = request.GET.get("category", "")
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    products = Product.objects.filter(is_active=True,is_approved=True) #products in stock and approved

    if query:
        products = products.filter(name__icontains=query)

    if brand:
        products = products.filter(seller__username__iexact=brand)

    if category:
        products = products.filter(category__name__iexact=category)

    if min_price:
        products = products.filter(price__gte=min_price) #gte is greater than or equal to

    if max_price:
        products = products.filter(price__lte=max_price) #lte is less than or equal to

    return render(request, "generic/catalog.html", {"products": products})


#this is renders the catalog page that is for admins and sellers, sellers will only see their own products, and admins will see all products approved or not
@login_required
def seller_admin_catalog(request):
    if request.user.role not in ["seller", "admin"]:
        return redirect("catalog")

    query = request.GET.get("query", "").strip()
    category = request.GET.get("category", "").strip()
    approval_status = request.GET.get("approval_status", "").strip()
    active_status = request.GET.get("is_active", "").strip()

    # admin sees everything
    if request.user.role == "admin":
        products = Product.objects.all().select_related("seller", "category")
    else:
        # seller only sees their own products
        products = Product.objects.filter(
            seller=request.user
        ).select_related("seller", "category")

    if query:
        products = products.filter(name__icontains=query)

    if category:
        products = products.filter(category__name__iexact=category)

    if approval_status:
        if approval_status == "approved":
            products = products.filter(is_approved=True)
        elif approval_status == "unapproved":
            products = products.filter(is_approved=False)
        elif approval_status == "pending":
            products = products.filter(approval_status="Pending")
        elif approval_status == "rejected":
            products = products.filter(approval_status="Rejected")

    if active_status:
        if active_status == "active":
            products = products.filter(is_active=True)
        elif active_status == "inactive":
            products = products.filter(is_active=False)

    return render(request, "generic/selleradmincatalog.html", {"products": products,})


def adminModeration(request):
    return render(request, "generic/adminModeration.html")

def orderConf(request):
    return render(request, "generic/orderConf.html")


@login_required
def orders(request):
    orders = Order.objects.filter(buyer=request.user).prefetch_related("items", "items__product", "items__seller", "shipping_address").order_by("-created_at")

    return render(request, "generic/orders.html", {"orders": orders,})


def returnReq(request):
    return render(request, "generic/returnReq.html")

def returns(request):
    return render(request, "generic/returns.html")

@login_required
def sellerInventory(request): 
    if request.user.role != "seller":
        return redirect("home")
    products = Product.objects.filter(seller=request.user).select_related("category")
    total = products.count()
    low_stock = products.filter(stock__range=(1, 2)).count()
    out_of_stock = products.filter(stock=0).count()
    return render(request, "generic/seller-inventory.html", {
        "products": products,
        "total": total,
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
    })

def sellerProducts(request, pk):
    from accounts.models import User
    seller = get_object_or_404(User, pk=pk)
    products = Product.objects.filter(seller=seller, is_active=True, is_approved=True)
    return render(request, "generic/seller-products.html", {"products": products, "seller": seller})



@login_required
def createProd(request): #made this because I made a new-item page for sellers
    if request.user.role != "seller":
        return redirect("home")

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.is_approved = False
            product.approval_status = "Pending" #product has to have admin approval
            # Check whether it's valid and save the data
            product.save()
            #html page for sellers will be created then linked to this
            return redirect('sellerInventory')
    else:
        # any other request method creates an empty form
        form = ProductForm()
        
    # pull up html page- needs to be named
    return render(request, "generic/new-item.html", {"form": form})

@login_required
def editProd(request, pk):
    if request.user.role != "seller":
        return redirect("home")
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == "POST":
        # updating price and stock requires no admin approval
        new_price = request.POST.get("price")
        new_stock = request.POST.get("stock")
        if new_price:
            product.price = new_price
        if new_stock:
            product.stock = new_stock
        
        # new name or description requires admin approval
        new_name = request.POST.get("name", "").strip()
        new_description = request.POST.get("description", "").strip()
        needs_review = False
        
        #if the name or description is added, store new value in a pending field and set approval status to pending
        if new_name and new_name != product.name:
            product.pending_name = new_name
            needs_review = True
        if new_description and new_description != product.description:
            product.pending_description = new_description
            needs_review = True
        if needs_review:
            product.approval_status = "Pending"
        
        product.save()
        return redirect("sellerInventory")
    return render(request, "generic/edit-item.html", {"product": product})

@login_required
def delistProd(request, pk):
    if request.user.role != "seller":
        return redirect("home")
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == "POST":
        product.is_active = False
        product.save()
    return redirect("sellerInventory")

def comparison(request):
    selected_ids = request.GET.getlist("compare")
    products= Product.objects.filter(id__in=selected_ids)
    return render ( request, "generic/comparison.html", {"products": products})

def prod_details(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "generic/product.html", {"product": product})


#started some work on the orders and checkout/ prob needs to be cleaned up
@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(buyer=request.user)
    cart_items = CartItem.objects.filter(cart=cart).select_related("product")

    if not cart_items.exists():
        return redirect("cart:cart_details")

    saved_addresses = Address.objects.filter(user=request.user)
    saved_payments = SavedPaymentMethod.objects.filter(user=request.user)

    subtotal = sum(item.product.price * item.quantity for item in cart_items)
    tax = subtotal * Decimal("0.07")
    fees = Decimal("6.99") #shipping fee 
    total = subtotal + tax + fees

    if request.method == "POST":
        selected_address = request.POST.get("saved_address")
        selected_payment = request.POST.get("saved_payment")

        if selected_address:
            shipping_address = Address.objects.get(id=selected_address)
        else:
            first = request.POST.get("first_name", "").strip()
            last = request.POST.get("last_name", "").strip()
            street = request.POST.get("street", "").strip()
            city = request.POST.get("city", "").strip()
            state = request.POST.get("state", "").strip()
            zipcode = request.POST.get("zipcode", "").strip()
            country = request.POST.get("country", "").strip()

            errors = {}

            if not first:
                errors["first_name"] = "First name is required."
            if not last:
                errors["last_name"] = "Last name is required."
            if not street:
                errors["street"] = "Street address is required."
            if not city:
                errors["city"] = "City is required."
            if not state:
                errors["state"] = "State is required."
            if not zipcode:
                errors["zipcode"] = "ZIP code is required."
            if not country:
                errors["country"] = "Country is required."

            if errors:
                return render(request, "generic/checkout.html", {"errors": errors,"cart_items": cart_items,"saved_addresses": saved_addresses,"saved_payments": saved_payments,"subtotal": subtotal,"tax": tax,"fees": fees,"total": total,})

            shipping_address = Address.objects.create(user=request.user,full_name=f"{first} {last}",street=street,city=city,state=state,zipcode=zipcode,country=country,)

        payment_method = request.POST.get("payment_method", "").strip()

        if not payment_method:
            return render(request, "generic/checkout.html", {
                "errors": {"payment_method": "Payment method is required."},
                "cart_items": cart_items,
                "saved_addresses": saved_addresses,
                "saved_payments": saved_payments,
                "subtotal": subtotal,
                "tax": tax,
                "fees": fees,
                "total": total,
            })

        # if user picked a saved payment method
        if selected_payment:
            saved_payment = SavedPaymentMethod.objects.get(id=selected_payment, user=request.user)
        else:
            cardholder_name = request.POST.get("cardholder_name", "").strip()
            card_brand = request.POST.get("card_brand", "").strip()
            card_number = request.POST.get("card_number", "").strip().replace(" ", "")
            exp_month = request.POST.get("exp_month", "").strip()
            exp_year = request.POST.get("exp_year", "").strip()
            save_payment = bool(request.POST.get("save_payment"))

            if save_payment and card_number:
                #creates a saved payment in db
                SavedPaymentMethod.objects.create(
                    user=request.user,cardholder_name=cardholder_name, card_brand=card_brand,card_last4=card_number[-4:],exp_month=exp_month,exp_year=exp_year,is_default=False,)
        #creates order in db
        order = Order.objects.create(buyer=request.user,shipping_address=shipping_address,subtotal=subtotal,tax=tax,total=total,)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                seller=item.product.seller,
                quantity=item.quantity,
                price_when_ordered=item.product.price,
            )
        #records payment in db
        Payment.objects.create(order=order,payment_method=payment_method,payment_status="Completed",)

        #wipes cart
        cart_items.delete()
        return redirect("orderConf")

    return render(request, "generic/checkout.html", {"errors": {},"cart_items": cart_items,"saved_addresses": saved_addresses,"saved_payments": saved_payments,"subtotal": subtotal,"tax": tax,"fees": fees,"total": total,})



#This is the address logic here, handles saving addresses to accounts, setting default shipping addresses, and deleting the addresses
@login_required
def addresses(request):
    errors = {}

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        street = request.POST.get("street", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        zipcode = request.POST.get("zipcode", "").strip()
        country = request.POST.get("country", "").strip()
        is_default = bool(request.POST.get("is_default"))

        if not full_name or not street or not city or not state or not zipcode or not country:
            errors["form"] = "Please fill out all required address fields."
        else:
            if is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

            Address.objects.create(user=request.user,full_name=full_name,street=street,city=city,state=state,zipcode=zipcode,country=country,is_default=is_default,)

            return redirect("addresses")

    addresses = Address.objects.filter(user=request.user)

    return render(request, "generic/addresses.html", {"addresses": addresses,"errors": errors,})

@login_required
def set_default_address(request, address_id):
    if request.method == "POST":
        address = get_object_or_404(Address, id=address_id, user=request.user)
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        address.is_default = True
        address.save()

    return redirect("addresses")

@login_required
def delete_address(request, address_id):
    if request.method == "POST":
        address = get_object_or_404(Address, id=address_id, user=request.user)
        try:
            address.delete()
        except ProtectedError:
           addresses = Address.objects.filter(user=request.user)
           return render(request, "generic/addresses.html", {"addresses": addresses,"errors": {"delete": "This address cannot be deleted because it is attached to an existing order."}})
    return redirect("addresses")

#this handles saved cards (debit credit cards)
@login_required
def billing(request):
    errors = {}

    if request.method == "POST":
        cardholder_name = request.POST.get("cardholder_name", "").strip()
        payment_method = request.POST.get("payment_method", "").strip()
        card_brand = request.POST.get("card_brand", "").strip()
        card_number = request.POST.get("card_number", "").strip().replace(" ", "")
        exp_month = request.POST.get("exp_month", "").strip()
        exp_year = request.POST.get("exp_year", "").strip()
        is_default = bool(request.POST.get("is_default"))

        if not cardholder_name or not payment_method or not card_brand or not card_number or not exp_month or not exp_year:
            errors["form"] = "Please fill out all required payment fields."
        else:
            if is_default:
                SavedPaymentMethod.objects.filter(user=request.user, is_default=True).update(is_default=False)

            SavedPaymentMethod.objects.create(user=request.user,cardholder_name=cardholder_name,card_brand=card_brand,card_last4=card_number[-4:],exp_month=exp_month,exp_year=exp_year,is_default=is_default,) #default card

            return redirect("billing")

    saved_payments = SavedPaymentMethod.objects.filter(user=request.user)

    return render(request, "generic/billing.html", {"saved_payments": saved_payments,"errors": errors,})

@login_required
def set_default_payment(request, payment_id):
    if request.method == "POST":
        payment = get_object_or_404(SavedPaymentMethod, id=payment_id, user=request.user)
        SavedPaymentMethod.objects.filter(user=request.user, is_default=True).update(is_default=False)
        payment.is_default = True
        payment.save()

    return redirect("billing")

@login_required
def delete_payment(request, payment_id):
    if request.method == "POST":
        payment = get_object_or_404(SavedPaymentMethod, id=payment_id, user=request.user)
        payment.delete()

    return redirect("billing")