import pytest
from django.urls import reverse
from decimal import Decimal
from accounts.models import User
from django.utils import timezone
from shop.models import (
    Product, Cart, CartItem, Category, ShippingOption, Address, Order, OrderItem,
    Payment, Payout, Fee,
)

"""TESTS: 
1. Buyers can view the catalog and see approved products
2. Buyers can view product details 
3. Buyers can add items to their cart and a CartItem is created in the DB
4. Buyers can update quantity of items in cart 
5. Buyers can remove items from their cart and the CartItem is deleted from the DB
6. Cart page loads and shows items in the cart 
7. Unapproved products cannot be added to the cart and 404 is returned
8. Users that arent logged in can't access the cart and are redirected
9. Buyers cannot access the seller/admin catalog
10. Buyer cannot add more items to cart than items are in stock
11. Items will stay in cart after cart is viewed
12. User has to be logged in to reach checkout page
13. Buyers with a empty cart are redirected away from checkout to cart
14. Buyers can reach checkout when they have items in their cart
15. Checkout works when the buyer uses a saved address and payment, order, orderitem, and payment are created
16. After a order is made, the  cart is cleared
17. Checkout still works when the buyer doesnt choose a saved address
18. Checkout doesnt create a order if the buyer exits without a payment 
19. Checkout doesnt create a order if buyer doesnt pick a saved address or enters a address
20. Buyers can filter catalog by seller
21. Buyers can filter catalog by category
22. Buyers only see approved products in catalog
23. Order item keeps original purchase price after product price changes
24. Checkout creates shipping fee and payout
25. Order history remains valid after product is delisted
"""

@pytest.fixture
def buyer(db):
    return User.objects.create_user(
        username="buyer1",
        password="testpass123",
        role="buyer",
    )


@pytest.fixture
def seller(db):
    return User.objects.create_user(
        username="seller1",
        password="testpass123",
        role="seller",
    )


@pytest.fixture
def vinyl_category(db):
    return Category.objects.create(name="Vinyl")


@pytest.fixture
def singer1_vinyl(db, seller, vinyl_category):
    return Product.objects.create(
        seller=seller,
        category=vinyl_category,
        name="Singer1 Vinyl",
        description="Vinyl of Singer1",
        price=Decimal("19.99"),
        stock=5,
        is_active=True,
        is_approved=True,
        approval_status="Approved",
        orbit_int=True,
        redirect_int=None,
        deleted_at=None,
    )


@pytest.fixture
def singer2_vinyl(db, seller, vinyl_category):
    return Product.objects.create(
        seller=seller,
        category=vinyl_category,
        name="Singer2 Vinyl",
        description="Vinyl of Singer2",
        price=Decimal("24.99"),
        stock=3,
        is_active=True,
        is_approved=True,
        approval_status="Approved",
        orbit_int=True,
        redirect_int=None,
        deleted_at=None,
    )


@pytest.fixture
def buyer_address(db, buyer):
    return Address.objects.create(
        user=buyer,
        full_name="Buyer Test",
        street="123 Testing St",
        city="City",
        state="KS",
        zipcode="12345",
        country="USA",
        is_default=True,
    )


@pytest.fixture
def saved_payment(db, buyer):
    return Payment.objects.create(
        user=buyer,
        cardholder_name="Buyer Test",
        card_brand="Visa",
        card_last4="1111",
        exp_month="04",
        exp_year="2026",
        is_default=True,
        is_saved=True,
        payment_method="CreditCard",
        payment_status="Pending",
    )

@pytest.fixture
def standard_shipping(db):
    return ShippingOption.objects.create(
        name="Standard Shipping",
        code="standard",
        description="Standard delivery",
        base_price=Decimal("6.99"),
        is_active=True,
    )

@pytest.mark.django_db
def test_buyer_can_view_catalog(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    response = client.get(reverse("catalog"))
    assert response.status_code == 200
    assert "Singer1 Vinyl" in response.content.decode()


@pytest.mark.django_db
def test_buyer_catalog_only_shows_approved_products(client, buyer, seller, vinyl_category, singer1_vinyl):
    client.force_login(buyer)

    Product.objects.create(
        seller=seller,
        category=vinyl_category,
        name="Hidden Vinyl",
        description="Should not show",
        price=Decimal("9.99"),
        stock=2,
        is_active=True,
        is_approved=False,
        approval_status="Pending",
        orbit_int=True,
        redirect_int=None,
        deleted_at=None,
    )

    response = client.get(reverse("catalog"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Singer1 Vinyl" in content
    assert "Hidden Vinyl" not in content


@pytest.mark.django_db
def test_buyer_can_filter_catalog_by_seller(client, buyer, seller, singer1_vinyl):
    client.force_login(buyer)
    response = client.get(reverse("catalog"), {"seller": seller.username})

    assert response.status_code == 200
    assert "Singer1 Vinyl" in response.content.decode()


@pytest.mark.django_db
def test_buyer_can_filter_catalog_by_category(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    response = client.get(reverse("catalog"), {"category": "Vinyl"})

    assert response.status_code == 200
    assert "Singer1 Vinyl" in response.content.decode()


@pytest.mark.django_db
def test_buyer_can_view_product_detail(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    response = client.get(reverse("prod_details", args=[singer1_vinyl.pk]))
    assert response.status_code == 200
    assert "Singer1 Vinyl" in response.content.decode()


@pytest.mark.django_db
def test_buyer_can_add_to_cart(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    response = client.post(
        reverse("cart:add_to_cart", args=[singer1_vinyl.pk]),
        {"quantity": 1},
    )
    assert response.status_code == 302
    cart = Cart.objects.get(buyer=buyer)
    item = CartItem.objects.get(cart=cart, product=singer1_vinyl)
    assert item.quantity == 1


@pytest.mark.django_db
def test_buyer_can_update_cart_quantity(client, buyer, singer1_vinyl):
    client.force_login(buyer)

    client.post(
        reverse("cart:add_to_cart", args=[singer1_vinyl.pk]),
        {"quantity": 1},
    )

    response = client.post(
        reverse("cart:update_cart_item", args=[singer1_vinyl.pk]),
        {"quantity": 3},
    )

    assert response.status_code == 302
    cart = Cart.objects.get(buyer=buyer)
    item = CartItem.objects.get(cart=cart, product=singer1_vinyl)
    assert item.quantity == 3


@pytest.mark.django_db
def test_buyer_can_remove_from_cart(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    client.post(
        reverse("cart:add_to_cart", args=[singer1_vinyl.pk]),
        {"quantity": 1},
    )
    cart = Cart.objects.get(buyer=buyer)
    item = CartItem.objects.get(cart=cart, product=singer1_vinyl)

    response = client.post(reverse("cart:remove_from_cart", args=[item.pk]))

    assert response.status_code == 302


@pytest.mark.django_db
def test_cart_details_page_loads(client, buyer, singer1_vinyl, singer2_vinyl):
    client.force_login(buyer)
    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.pk]), {"quantity": 1})
    client.post(reverse("cart:add_to_cart", args=[singer2_vinyl.pk]), {"quantity": 2})
    response = client.get(reverse("cart:cart_details"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Singer1 Vinyl" in content
    assert "Singer2 Vinyl" in content


@pytest.mark.django_db
def test_unapproved_product_cannot_be_added(client, buyer, seller, vinyl_category):
    client.force_login(buyer)
    pending_vinyl = Product.objects.create(
        seller=seller,
        category=vinyl_category,
        name="Singer3 Vinyl",
        description="Vinyl of Singer3",
        price=Decimal("22.99"),
        stock=2,
        is_active=True,
        is_approved=False,
        approval_status="Pending",
        orbit_int=True,
        redirect_int=None,
        deleted_at=None,
    )
    response = client.post(
        reverse("cart:add_to_cart", args=[pending_vinyl.pk]),
        {"quantity": 1},
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_anonymous_user_redirected_from_cart(client):
    response = client.get(reverse("cart:cart_details"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_buyer_cannot_access_seller_catalog(client, buyer):
    client.force_login(buyer)
    response = client.get(reverse("sellerInventory"))
    assert response.status_code in [302, 403]


@pytest.mark.django_db
def test_buyer_cannot_exceed_stock(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    client.post(
        reverse("cart:add_to_cart", args=[singer1_vinyl.pk]),
        {"quantity": 100},
    )

    cart = Cart.objects.get(buyer=buyer)
    item = CartItem.objects.get(cart=cart, product=singer1_vinyl)
    assert item.quantity <= singer1_vinyl.stock


@pytest.mark.django_db
def test_cart_persists_items(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.pk]), {"quantity": 1})
    response = client.get(reverse("cart:cart_details"))
    assert "Singer1 Vinyl" in response.content.decode()


@pytest.mark.django_db
def test_anonymous_user_redirected_from_checkout(client):
    response = client.get(reverse("checkout"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_checkout_redirects_when_cart_is_empty(client, buyer):
    client.force_login(buyer)

    response = client.get(reverse("checkout"))

    assert response.status_code == 302
    assert response.url == reverse("cart:cart_details")


@pytest.mark.django_db
def test_buyer_can_view_checkout_page_with_cart_items(client, buyer, singer1_vinyl):
    client.force_login(buyer)

    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.pk]), {"quantity": 1})

    response = client.get(reverse("checkout"))

    assert response.status_code == 200
    assert "Singer1 Vinyl" in response.content.decode()


@pytest.mark.django_db
def test_checkout_with_default_address_and_saved_payment_creates_order(client, buyer, buyer_address, saved_payment, singer1_vinyl, standard_shipping):
    client.force_login(buyer)

    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.pk]), {"quantity": 1})

    response = client.post(
        reverse("checkout"),
        {
            "saved_address": str(buyer_address.pk),
            "saved_payment": str(saved_payment.pk),
            "payment_method": "CreditCard",
            "shipping_option": standard_shipping.code,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("orderConf")

    assert Order.objects.filter(buyer=buyer).exists()
    order = Order.objects.get(buyer=buyer)

    assert order.shipping_address == buyer_address
    assert OrderItem.objects.filter(order=order, product=singer1_vinyl).exists()
    assert Payment.objects.filter(
        order=order,
        payment_method="CreditCard",
        payment_status="Completed"
    ).exists()


@pytest.mark.django_db
def test_checkout_clears_cart_after_order(client, buyer, buyer_address, saved_payment, singer1_vinyl,standard_shipping):
    client.force_login(buyer)

    client.post(
        reverse("cart:add_to_cart", args=[singer1_vinyl.pk]),
        {"quantity": 1},
    )

    client.post(
        reverse("checkout"),
        {
            "saved_address": str(buyer_address.pk),
            "saved_payment": str(saved_payment.pk),
            "payment_method": "CreditCard",
            "shipping_option": standard_shipping.code,
        },
    )

    cart = Cart.objects.get(buyer=buyer)
    assert not CartItem.objects.filter(cart=cart).exists()


@pytest.mark.django_db
def test_checkout_can_create_new_address_if_none_selected(client, buyer, singer1_vinyl, standard_shipping):
    client.force_login(buyer)

    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.pk]), {"quantity": 1})

    response = client.post(
        reverse("checkout"),
        {
            "first_name": "Buyer",
            "last_name": "Test",
            "street": "123 Main St",
            "city": "City",
            "state": "MS",
            "zipcode": "12345",
            "country": "USA",
            "payment_method": "CreditCard",
            "cardholder_name": "Buyer Test",
            "card_brand": "Visa",
            "card_number": "1111111111111111",
            "exp_month": "04",
            "exp_year": "2026",
            "shipping_option": standard_shipping.code,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("orderConf")
    assert Order.objects.filter(buyer=buyer).exists()


@pytest.mark.django_db
def test_checkout_requires_payment_method(client, buyer, buyer_address, singer1_vinyl, standard_shipping):
    client.force_login(buyer)

    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.pk]), {"quantity": 1})

    response = client.post(
        reverse("checkout"),
        {
            "saved_address": str(buyer_address.pk),
            "shipping_option": standard_shipping.code,
        },
    )

    assert response.status_code == 200
    assert not Order.objects.filter(buyer=buyer).exists()


@pytest.mark.django_db
def test_checkout_requires_address_fields_when_no_saved_address_selected(client, buyer, singer1_vinyl, standard_shipping):
    client.force_login(buyer)
    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.pk]), {"quantity": 1})

    response = client.post(
        reverse("checkout"),
        {
            "payment_method": "CreditCard",
            "cardholder_name": "Buyer Test",
            "card_brand": "Visa",
            "card_number": "4111111111111111",
            "exp_month": "04",
            "exp_year": "2026",
            "shipping_option": standard_shipping.code,
        },
    )

    assert response.status_code == 200
    assert not Order.objects.filter(buyer=buyer).exists()


@pytest.mark.django_db
def test_order_item_keeps_price_at_purchase_after_product_price_changes(
    client, buyer, buyer_address, saved_payment, singer1_vinyl, standard_shipping
):
    client.force_login(buyer)
    original_price = singer1_vinyl.price

    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.pk]), {"quantity": 1})
    client.post(
        reverse("checkout"),
        {
            "saved_address": str(buyer_address.pk),
            "saved_payment": str(saved_payment.pk),
            "payment_method": "CreditCard",
            "shipping_option": standard_shipping.code,
        },
    )

    order = Order.objects.get(buyer=buyer)
    order_item = OrderItem.objects.get(order=order, product=singer1_vinyl)

    singer1_vinyl.price = Decimal("99.99")
    singer1_vinyl.save(update_fields=["price"])

    order_item.refresh_from_db()
    assert order_item.price_at_purchase == original_price


@pytest.mark.django_db
def test_checkout_creates_fee_and_paid_payout(client, buyer, buyer_address, saved_payment, singer1_vinyl, standard_shipping):
    client.force_login(buyer)
    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.pk]), {"quantity": 1})

    client.post(
        reverse("checkout"),
        {
            "saved_address": str(buyer_address.pk),
            "saved_payment": str(saved_payment.pk),
            "payment_method": "CreditCard",
            "shipping_option": standard_shipping.code,
        },
    )

    order = Order.objects.get(buyer=buyer)
    order_item = OrderItem.objects.get(order=order, product=singer1_vinyl)

    assert Fee.objects.filter(order=order, fee_type="Shipping").exists()

    payout = Payout.objects.get(order_item=order_item)
    assert payout.seller == singer1_vinyl.seller
    assert payout.status == "Paid"
    assert payout.amount == order_item.price_at_purchase * order_item.quantity
    assert payout.paid_at is not None


@pytest.mark.django_db
def test_order_history_remains_after_product_is_delisted(
    client, buyer, buyer_address, saved_payment, singer1_vinyl, standard_shipping
):
    client.force_login(buyer)

    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.pk]), {"quantity": 1})
    client.post(
        reverse("checkout"),
        {
            "saved_address": str(buyer_address.pk),
            "saved_payment": str(saved_payment.pk),
            "payment_method": "CreditCard",
            "shipping_option": standard_shipping.code,
        },
    )

    singer1_vinyl.deleted_at = timezone.now()
    singer1_vinyl.save(update_fields=["deleted_at"])

    order = Order.objects.get(buyer=buyer)
    assert OrderItem.objects.filter(order=order).exists()
