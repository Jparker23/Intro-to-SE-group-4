from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.contrib.auth import get_user_model
from decimal import Decimal
from .models import Product, Address, Order, Category, OrderItem, Payment, Cart, CartItem, Fee, ReturnRequest
from .forms import ProductForm
from django.db import transaction
from django.utils import timezone


TAX_RATE_PERCENT = Decimal("10.00")
TAX_RATE_DECIMAL = Decimal("0.10")
DEFAULT_SHIPPING_FEE = Decimal("6.99")


def _buyer_visible_products():
    return Product.objects.filter(is_active=True,is_approved=True,orbit_int=True,redirect_int__isnull=True,deleted_at__isnull=True,)


def home(request):
    #approved and in stock products on the home page
    User = get_user_model()
    featured_products = _buyer_visible_products().filter(stock__gt=0)[:4]
    sellers = User.objects.filter(role="seller").order_by("username")
    return render(request, "generic/home.html", {"featured_products": featured_products,"sellers": sellers,})

def brandResults(request, brand):
    return render(request, "generic/brandResults.html", {"brand": brand})

def catalog(request):
    return render(request, "generic/catalog.html")

#this is a catalog ONLY for buyers
def buyer_only_catalog(request):
    User = get_user_model()
    sellers = User.objects.filter(role="seller").order_by("username")
    query = request.GET.get("query", "").strip() #product name get from search bar
    brand = request.GET.get("seller", "").strip()
    category = request.GET.get("category", "")
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    products = _buyer_visible_products().select_related("seller", "category") #products in stock and approved

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

    return render(request, "generic/catalog.html", {"products": products, "sellers":sellers,})


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
        products = Product.objects.all().select_related("seller", "category", "redirect_int")
    else:
        # seller only sees their own products
        products = Product.objects.filter(seller=request.user).select_related("seller", "category", "redirect_int")

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
    user_orders = (Order.objects.filter(buyer=request.user).select_related("shipping_address").prefetch_related("items", "items__product", "items__seller", "payments", "fees").order_by("-created_at"))

    return render(request, "generic/orders.html", {"orders": user_orders,})


@login_required
def returns(request):
    user_returns = ReturnRequest.objects.filter(
        buyer=request.user
    ).select_related(
        "order_item", "order_item__product"
    ).order_by("-created_at")
    return render(request, "generic/returns.html", {"returns": user_returns})


@login_required
def returnReq(request):
    order_item_id = request.GET.get("order_item_id") or request.POST.get("order_item_id")
    order_item = get_object_or_404(OrderItem, id=order_item_id, order__buyer=request.user)

    existing = ReturnRequest.objects.filter(buyer=request.user, order_item=order_item).first()
    if existing:
        return redirect("returns")

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()
        if reason:
            ReturnRequest.objects.create(
                buyer=request.user,
                order_item=order_item,
                reason=reason,
                status="Pending",
                refund_amount=order_item.price_at_purchase * order_item.quantity,
            )
            return redirect("returns")

    return render(request, "generic/returnReq.html", {"order_item": order_item})
@login_required
def sellerInventory(request): 
    if request.user.role != "seller":
        return redirect("home")
    
    products = Product.objects.filter(seller=request.user).select_related("category", "redirect_int")
    total = products.count()
    low_stock = products.filter(stock__range=(1, 2), deleted_at__isnull=True).count()
    out_of_stock = products.filter(stock=0, deleted_at__isnull=True).count()
    return render(request, "generic/seller-inventory.html", {"products": products, "total": total, "low_stock": low_stock, "out_of_stock": out_of_stock,})

def sellerProducts(request, pk):
    User = get_user_model()
    seller = get_object_or_404(User, pk=pk)
    products = _buyer_visible_products().filter(seller=seller)
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
            product.orbit_int = True
            product.redirect_int = None
            product.deleted_at = None
            # Check whether it's valid and save the data
            product.save()
            #html page for sellers will be created then linked to this
            return redirect("sellerInventory")
    else:
        # any other request method creates an empty form
        form = ProductForm(request.POST, request.FILES)
        
    # pull up html page- needs to be named
    return render(request, "generic/new-item.html", {"form": form})

@login_required
def editProd(request, pk):
    if request.user.role != "seller":
        return redirect("home")
    
    product = get_object_or_404(Product, pk=pk, seller=request.user, deleted_at__isnull=True,)
    categories = Category.objects.all()
    
    if request.method == "POST":
        new_name = request.POST.get("name", "").strip() or product.name
        new_description = request.POST.get("description", "").strip() or product.description
        new_price_raw = request.POST.get("price", "").strip()
        new_stock_raw = request.POST.get("stock", "").strip()
        new_category_id = request.POST.get("category", "").strip()
        new_orbit_raw = request.POST.get("orbit_int", "").strip()

        new_price = Decimal(new_price_raw) if new_price_raw else product.price
        new_stock = int(new_stock_raw) if new_stock_raw else product.stock
        new_photo = request.FILES.get("photo")
        photo_changed = new_photo is not None

        if new_photo:
            product.photo = new_photo

        if new_category_id:
            try:
                new_category_id = int(new_category_id)
            except ValueError:
                new_category_id = None
        new_category = product.category
        if new_category_id is not None:
            new_category = Category.objects.filter(pk=new_category_id).first()

        if new_orbit_raw:
            new_orbit = new_orbit_raw.lower() in ["1", "true", "yes", "on"]
        else:
            new_orbit = product.orbit_int

        visibility_changed = new_orbit != product.orbit_int
        stock_changed = new_stock != product.stock

        other_fields_changed = any([new_name != product.name,new_description != product.description,new_price != product.price,new_category != product.category,photo_changed,])

        # Only stock/visibility updates happen on the same row.
        if not other_fields_changed:
            updated_fields = []

            if stock_changed:
                product.stock = new_stock
                updated_fields.append("stock")

            if visibility_changed:
                product.orbit_int = new_orbit
                updated_fields.append("orbit_int")

            if updated_fields:
                product.save(update_fields=updated_fields)

            return redirect("sellerInventory")

        # All other edits create a new row and redirect the old row to it.
        with transaction.atomic():
            new_product = Product.objects.create(seller=product.seller,category=new_category,name=new_name,description=new_description,price=new_price,stock=new_stock,photo= new_photo if new_photo else product.photo, is_active=True,is_approved=False,approval_status="Pending",orbit_int=True,)

            product.redirect_int  = new_product
            product.orbit_int = False
            product.save(update_fields=["redirect_int", "orbit_int"])

        return redirect("sellerInventory")

    return render(request, "generic/edit-item.html", {"product": product, "categories": categories})

  
@login_required
def delistProd(request, pk):
    if request.user.role != "seller":
        return redirect("home")
    product = get_object_or_404(Product, pk=pk, seller=request.user, deleted_at__isnull=True)
    if request.method == "POST":
         product.deleted_at = timezone.now()
         product.save(update_fields=["deleted_at"])
    return redirect("sellerInventory")

def comparison(request):
    selected_ids = request.GET.getlist("compare")
    products = _buyer_visible_products().filter(id__in=selected_ids)
    return render ( request, "generic/comparison.html", {"products": products})

def prod_details(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.deleted_at is not None:
        return redirect("catalog")

    if product.redirect_int is not None:
        return redirect("prod_details", pk=product.redirect_int.pk)

    return render(request, "generic/product.html", {"product": product})


@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(buyer=request.user)
    cart_items = CartItem.objects.filter(cart=cart).select_related("product", "product__seller")

    if not cart_items.exists():
        return redirect("cart:cart_details")

    saved_addresses = Address.objects.filter(user=request.user)
    saved_payments = Payment.objects.filter(user=request.user, is_saved=True).order_by("-is_default", "-payment_date")    
    errors = {}
    
    invalid_items = []
    for item in cart_items:
        product = item.product
        if (product.deleted_at is not None or not product.is_active or not product.is_approved or not product.orbit_int or product.redirect_int_id is not None) : 
            invalid_items.append(f"{product.name} is no longer available.")
        elif item.quantity > product.stock:
            invalid_items.append(f"{product.name} does not have enough stock.")

    if invalid_items:
        return render(request,"generic/checkout.html", {"errors": {"cart": " ".join(invalid_items)},"cart_items": cart_items,"saved_addresses": saved_addresses,"saved_payments": saved_payments,"subtotal": Decimal("0.00"),"tax": Decimal("0.00"),"fees": Decimal("0.00"),"total": Decimal("0.00"),},)
    
    subtotal = sum((item.product.price * item.quantity for item in cart_items), Decimal("0.00"))
    tax = (subtotal * TAX_RATE_DECIMAL)
    fees = DEFAULT_SHIPPING_FEE
    total = (subtotal + tax + fees)

    if request.method == "POST":
        selected_address = request.POST.get("saved_address")
        selected_payment = request.POST.get("saved_payment")

        errors = {}
        if selected_address:
            shipping_address = get_object_or_404(Address, id=selected_address, user=request.user)
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

            shipping_address = None
            if not errors:
                shipping_address = Address.objects.create(user=request.user,full_name=f"{first} {last}", street=street,city=city,state=state,zipcode=zipcode,country=country,is_default=False,)

        selected_saved_payment = None
        payment_method = request.POST.get("payment_method", "").strip()

        cardholder_name = ""
        card_brand = ""
        card_last4 = ""
        exp_month = ""
        exp_year = ""

        if selected_payment:
            selected_saved_payment = get_object_or_404(
                Payment,
                id=selected_payment,
                user=request.user,
                is_saved=True,
            )
            payment_method = selected_saved_payment.payment_method

        if not payment_method:
            errors["payment_method"] = "Payment method is required."

        cardholder_name = ""
        card_brand = ""
        card_last4 = ""
        exp_month = ""
        exp_year = ""

        if selected_payment:
            selected_saved_payment = get_object_or_404(Payment,id=selected_payment,user=request.user,is_saved=True,)
            payment_method = selected_saved_payment.payment_method
            cardholder_name = selected_saved_payment.cardholder_name
            card_brand = selected_saved_payment.card_brand
            card_last4 = selected_saved_payment.card_last4
            exp_month = selected_saved_payment.exp_month
            exp_year = selected_saved_payment.exp_year
        else:
            cardholder_name = request.POST.get("cardholder_name", "").strip()
            card_brand = request.POST.get("card_brand", "").strip()
            card_number = request.POST.get("card_number", "").strip().replace(" ", "")
            exp_month = request.POST.get("exp_month", "").strip()
            exp_year = request.POST.get("exp_year", "").strip()
            save_payment = bool(request.POST.get("save_payment"))

            if not payment_method:
                errors["payment_method"] = "Payment method is required."
            if not cardholder_name:
                errors["cardholder_name"] = "Cardholder name is required."
            if not card_brand:
                errors["card_brand"] = "Card brand is required."
            if not card_number:
                errors["card_number"] = "Card number is required."
            if not exp_month:
                errors["exp_month"] = "Expiration month is required."
            if not exp_year:
                errors["exp_year"] = "Expiration year is required."

            if card_number:
                card_last4 = card_number[-4:]

        if errors:
            return render(request,"generic/checkout.html",{"errors": errors,"cart_items": cart_items,"saved_addresses": saved_addresses,"saved_payments": saved_payments,"subtotal": subtotal,"tax": tax,"fees": fees,"total": total,},)

       
        # Create order + items + payment
        with transaction.atomic():
            order = Order.objects.create(buyer=request.user,shipping_address=shipping_address,subtotal=subtotal,tax_rate=TAX_RATE_PERCENT,tax=tax,fee=fees,total=total,status="Processing",)

            for item in cart_items:
                if item.quantity > item.product.stock:
                    raise ValueError(f"{item.product.name} does not have enough stock.")

                OrderItem.objects.create(order=order,product=item.product,seller=item.product.seller,quantity=item.quantity,price_at_purchase=item.product.price,status="Processing",)

                item.product.stock -= item.quantity
                item.product.save(update_fields=["stock"])

            Fee.objects.create(order=order,fee_type="Shipping",amount=fees,)

            # Save card for future use only if user entered a new one and checked save
            if not selected_saved_payment and bool(request.POST.get("save_payment")):
                Payment.objects.create(user=request.user,order=None,payment_method=payment_method,payment_status="Pending",cardholder_name=cardholder_name,card_brand=card_brand,card_last4=card_last4,exp_month=exp_month,exp_year=exp_year,is_saved=True,is_default=False,)

            # Actual payment record for the order
            Payment.objects.create(user=request.user,order=order,payment_method=payment_method,payment_status="Completed",cardholder_name=cardholder_name,card_brand=card_brand,card_last4=card_last4,exp_month=exp_month,exp_year=exp_year,is_saved=False,is_default=False,)

            cart_items.delete()

        return redirect("orderConf")

    return render(request,"generic/checkout.html",{"errors": {},"cart_items": cart_items,"saved_addresses": saved_addresses,"saved_payments": saved_payments,"subtotal": subtotal,"tax": tax,"fees": fees,"total": total,},)


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

    user_addresses = Address.objects.filter(user=request.user)

    return render(request, "generic/addresses.html", {"addresses": user_addresses,"errors": errors,})

@login_required
def set_default_address(request, address_id):
    if request.method == "POST":
        address = get_object_or_404(Address, id=address_id, user=request.user)
        Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
        address.is_default = True
        address.save(update_fields=["is_default"])

    return redirect("addresses")

@login_required
def delete_address(request, address_id):
    if request.method == "POST":
        address = get_object_or_404(Address, id=address_id, user=request.user)
        try:
            address.delete()
        except ProtectedError:
           user_addresses = Address.objects.filter(user=request.user)
           return render(request, "generic/addresses.html", {"addresses": user_addresses,"errors": {"delete": "This address cannot be deleted because it is attached to an existing order."}})
    return redirect("addresses")

#this handles saved cards (debit credit cards)
@login_required
def billing(request):
    errors = {}

    saved_payments = Payment.objects.filter(user=request.user,is_saved=True).order_by("-is_default", "-payment_date")


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
                Payment.objects.filter(user=request.user, is_default=True).update(is_default=False)

            Payment.objects.create(user=request.user,cardholder_name=cardholder_name,card_brand=card_brand,card_last4=card_number[-4:],exp_month=exp_month,exp_year=exp_year,is_default=is_default,) #default card

            return redirect("billing")

        saved_payments = Payment.objects.filter(user=request.user, is_saved=True).order_by("-is_default", "-payment_date")
    return render(request, "generic/billing.html", {"saved_payments": saved_payments,"errors": errors,})

@login_required
def set_default_payment(request, payment_id):
    if request.method == "POST":
        payment = get_object_or_404(Payment, id=payment_id, user=request.user, is_saved=True)
        Payment.objects.filter(user=request.user, is_default=True).update(is_default=False)
        payment.is_default = True
        payment.save(update_fields=["is_default"])

    return redirect("billing")

@login_required
def delete_payment(request, payment_id):
    if request.method == "POST":
        payment = get_object_or_404(Payment, id=payment_id, user=request.user, is_saved=True)
        payment.delete()

    return redirect("billing")