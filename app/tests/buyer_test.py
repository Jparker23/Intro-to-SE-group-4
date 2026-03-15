import pytest
from django.urls import reverse
from accounts.models import User
from shop.models import Product, Cart, CartItem, Category, Address, Order, OrderItem, Payment, SavedPaymentMethod

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
15. Checkout works when the buyr uses a saved address and payment, order, orderitem, and payment are created
16. After a order is made, the  cart is cleared
17. Checkout still works when the buyer doesnt choose a saved address
18. Checkout doesnt create a order if the buyer exits without a payment 
19. Checkout doesnt create a order if buyer doesnt pick a saved address or enters a address
"""

@pytest.fixture
def buyer(db):
    return User.objects.create_user(username="buyer1",password="testpass123",role="buyer",)


@pytest.fixture
def seller(db):
    return User.objects.create_user(username="seller1",password="testpass123",role="seller",)


@pytest.fixture
def vinyl_category(db):
    return Category.objects.create(name="Vinyl")


@pytest.fixture
def singer1_vinyl(db, seller, vinyl_category):
    return Product.objects.create(seller=seller,category=vinyl_category,name="Singer1 Vinyl",description="Vinyl of Singer1",price=19.99,stock=5,is_active=True,is_approved=True,approval_status="Approved",)


@pytest.fixture
def singer2_vinyl(db, seller, vinyl_category):
    return Product.objects.create(seller=seller,category=vinyl_category,name="Singer2 Vinyl",description="Vinyl of Singer2",price=24.99,stock=3,is_active=True,is_approved=True,approval_status="Approved",)

@pytest.fixture
def buyer_address(db, buyer):
    return Address.objects.create(user=buyer,full_name="Buyer Test",street="123 Main St",city="City",state="MS",zipcode="12345",country="USA",is_default=True,)

@pytest.fixture
def saved_payment(db, buyer):
    return SavedPaymentMethod.objects.create(user=buyer,cardholder_name="Buyer Test",card_brand="Visa",card_last4="1111",exp_month="04",exp_year="2026",is_default=True,)

@pytest.mark.django_db
def test_buyer_can_view_catalog(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    response = client.get(reverse("catalog"))
    assert response.status_code == 200
    assert "Singer1 Vinyl" in response.content.decode()


@pytest.mark.django_db
def test_buyer_can_view_product_detail(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    response = client.get(reverse("product_detail", args=[singer1_vinyl.id]))
    assert response.status_code == 200
    assert "Singer1 Vinyl" in response.content.decode()


@pytest.mark.django_db
def test_buyer_can_add_to_cart(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    response = client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.id]),{"quantity": 1},)
    assert response.status_code == 302
    cart = Cart.objects.get(buyer=buyer)
    item = CartItem.objects.get(cart=cart, product=singer1_vinyl)
    assert item.quantity == 1


@pytest.mark.django_db
def test_buyer_can_update_cart_quantity(client, buyer, singer1_vinyl):
    client.force_login(buyer)

    client.post(
        reverse("cart:add_to_cart", args=[singer1_vinyl.id]),{"quantity": 1},)

    response = client.post(
        reverse("cart:update_cart_item", args=[singer1_vinyl.id]),{"quantity": 3},)

    assert response.status_code == 302
    cart = Cart.objects.get(buyer=buyer)
    item = CartItem.objects.get(cart=cart, product=singer1_vinyl)
    assert item.quantity == 3


@pytest.mark.django_db
def test_buyer_can_remove_from_cart(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    client.post( reverse("cart:add_to_cart", args=[singer1_vinyl.id]), {"quantity": 1},)
    cart = Cart.objects.get(buyer=buyer)
    item = CartItem.objects.get(cart=cart, product=singer1_vinyl)
    response = client.get(reverse("cart:remove_from_cart", args=[item.id]))
    assert response.status_code == 302
    assert not CartItem.objects.filter(id=item.id).exists()


@pytest.mark.django_db
def test_cart_details_page_loads(client, buyer, singer1_vinyl, singer2_vinyl):
    client.force_login(buyer)
    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.id]), {"quantity": 1})
    client.post(reverse("cart:add_to_cart", args=[singer2_vinyl.id]), {"quantity": 2})
    response = client.get(reverse("cart:cart_details"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "Singer1 Vinyl" in content
    assert "Singer2 Vinyl" in content


@pytest.mark.django_db
def test_unapproved_product_cannot_be_added(client, buyer, seller, vinyl_category):
    client.force_login(buyer)
    pending_vinyl = Product.objects.create(seller=seller,category=vinyl_category,name="Singer3 Vinyl",description="Vinyl of Singer3",price=22.99,stock=2,is_active=True,is_approved=False, approval_status="Pending",)
    response = client.post(reverse("cart:add_to_cart", args=[pending_vinyl.id]),{"quantity": 1},)
    assert response.status_code == 404


@pytest.mark.django_db
def test_anonymous_user_redirected_from_cart(client):
    response = client.get(reverse("cart:cart_details"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_buyer_cannot_access_seller_catalog(client, buyer):
    client.force_login(buyer)
    response = client.get(reverse("seller_admin_catalog"))
    assert response.status_code in [302, 403]

@pytest.mark.django_db
def test_buyer_cannot_exceed_stock(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    response = client.post(
        reverse("cart:add_to_cart", args=[singer1_vinyl.id]),{"quantity": 100},)

    cart = Cart.objects.get(buyer=buyer)
    item = CartItem.objects.get(cart=cart, product=singer1_vinyl)
    assert item.quantity <= singer1_vinyl.stock

@pytest.mark.django_db
def test_cart_persists_items(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.id]), {"quantity": 1})
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

    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.id]),{"quantity": 1},)

    response = client.get(reverse("checkout"))

    assert response.status_code == 200
    assert "Singer1 Vinyl" in response.content.decode()


@pytest.mark.django_db
def test_checkout_with_default_address_and_saved_payment_creates_order(client, buyer, buyer_address, saved_payment, singer1_vinyl):
    client.force_login(buyer)

    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.id]),{"quantity": 1},)

    response = client.post(
        reverse("checkout"),{"saved_address": str(buyer_address.id),"saved_payment": str(saved_payment.id),"payment_method": "CreditCard",},)

    assert response.status_code == 302
    assert response.url == reverse("orderConf")

    assert Order.objects.filter(buyer=buyer).exists()
    order = Order.objects.get(buyer=buyer)

    assert order.shipping_address == buyer_address
    assert OrderItem.objects.filter(order=order, product=singer1_vinyl).exists()
    assert Payment.objects.filter(order=order, payment_method="CreditCard", payment_status="Completed").exists()


@pytest.mark.django_db
def test_checkout_clears_cart_after_order(client, buyer, buyer_address, saved_payment, singer1_vinyl):
    client.force_login(buyer)

    client.post(
        reverse("cart:add_to_cart", args=[singer1_vinyl.id]),{"quantity": 1},)

    client.post(
        reverse("checkout"),{"saved_address": str(buyer_address.id),"saved_payment": str(saved_payment.id),"payment_method": "CreditCard",},)

    cart = Cart.objects.get(buyer=buyer)
    assert not CartItem.objects.filter(cart=cart).exists()


@pytest.mark.django_db
def test_checkout_can_create_new_address_if_none_selected(client, buyer, singer1_vinyl):
    client.force_login(buyer)

    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.id]),{"quantity": 1},)

    response = client.post(reverse("checkout"),{"first_name": "Buyer","last_name": "Test","street": "123 Main St","city": "City","state": "MS","zipcode": "12345","country": "USA","payment_method": "CreditCard","cardholder_name": "Buyer Test","card_brand": "Visa","card_number": "1111111111111111","exp_month": "04","exp_year": "2026",},)

    assert response.status_code == 302
    assert response.url == reverse("orderConf")
    assert Order.objects.filter(buyer=buyer).exists()


@pytest.mark.django_db
def test_checkout_requires_payment_method(client, buyer, buyer_address, singer1_vinyl):
    client.force_login(buyer)

    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.id]),{"quantity": 1},)

    response = client.post(
        reverse("checkout"),{"saved_address": str(buyer_address.id),},)

    assert response.status_code == 200
    assert not Order.objects.filter(buyer=buyer).exists()


@pytest.mark.django_db
def test_checkout_requires_address_fields_when_no_saved_address_selected(client, buyer, singer1_vinyl):
    client.force_login(buyer)
    client.post(reverse("cart:add_to_cart", args=[singer1_vinyl.id]),{"quantity": 1},)

    response = client.post(
        reverse("checkout"),
        {"payment_method": "CreditCard","cardholder_name": "Buyer Test","card_brand": "Visa","card_number": "4111111111111111", "exp_month": "04","exp_year": "2026",},)

    assert response.status_code == 200
    assert not Order.objects.filter(buyer=buyer).exists()