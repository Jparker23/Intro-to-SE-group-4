import pytest
from django.urls import reverse
from decimal import Decimal
from accounts.models import User
from shop.models import Product, Payout, Category, Order, OrderItem, Payment, Address



"""TESTS:
1. Sellers can access their inventory page
2. Buyers cannot access the seller inventory page
3. Sellers only see their own products in inventory
4. Sellers can create a new product
5. New seller products are saved as pending approval
6. Sellers can update stock immediately
7. Sellers editing the product name creates a pending replacement product
8. Sellers can delist a product
9. Delisted products no longer show in seller inventory
10. Seller storefront only shows buyer-visible products
11. Pending products do not show on the public seller storefront
12. Sellers can view their payouts page
13. Sellers only see their own payouts
"""


@pytest.fixture
def seller(db):
    return User.objects.create_user(
        username="seller1",
        password="testpass123",
        role="seller",
        first_name="Seller",
        last_name="Test",
        email="seller1@test.com",
    )


@pytest.fixture
def buyer(db):
    return User.objects.create_user(
        username="buyer1",
        password="testpass123",
        role="buyer",
        first_name="Buyer",
        last_name="Test",
        email="buyer1@test.com",
    )

@pytest.fixture
def category(db):
    return Category.objects.create(name="Vinyl")


@pytest.fixture
def seller_product(db, seller, category):
    return Product.objects.create(
        seller=seller,
        category=category,
        name="Seller Item",
        description="Seller item description",
        price=Decimal("25.00"),
        stock=2,
        is_active=True,
        is_approved=True,
        approval_status="Approved",
        orbit_int=True,
        redirect_int=None,
        deleted_at=None,
    )


@pytest.fixture
def pending_product(db, seller, category):
    return Product.objects.create(
        seller=seller,
        category=category,
        name="Pending Item",
        description="Pending item description",
        price=Decimal("10.00"),
        stock=2,
        is_active=True,
        is_approved=False,
        approval_status="Pending",
        orbit_int=True,
        redirect_int=None,
        deleted_at=None,
    )


@pytest.mark.django_db
def test_seller_can_access_inventory_page(client, seller, seller_product):
    client.force_login(seller)
    response = client.get(reverse("sellerInventory"))

    assert response.status_code == 200
    assert "Seller Item" in response.content.decode()


@pytest.mark.django_db
def test_buyer_cannot_access_seller_inventory(client, buyer):
    client.force_login(buyer)
    response = client.get(reverse("sellerInventory"))

    assert response.status_code == 302


@pytest.mark.django_db
def test_seller_inventory_shows_only_own_products(client, seller, category):
    other_seller = User.objects.create_user(
        username="seller2",
        password="testpass123",
        role="seller",
        email="seller2@test.com",
    )

    Product.objects.create(
        seller=seller,
        category=category,
        name="Mine",
        description="mine",
        price=Decimal("10.00"),
        stock=1,
        is_active=True,
        is_approved=True,
        approval_status="Approved",
        orbit_int=True,
    )

    Product.objects.create(
        seller=other_seller,
        category=category,
        name="Not Mine",
        description="not mine",
        price=Decimal("10.00"),
        stock=1,
        is_active=True,
        is_approved=True,
        approval_status="Approved",
        orbit_int=True,
    )

    client.force_login(seller)
    response = client.get(reverse("sellerInventory"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Mine" in content
    assert "Not Mine" not in content


@pytest.mark.django_db
def test_seller_inventory_stats_display(client, seller, category):
    Product.objects.create(
        seller=seller,
        category=category,
        name="Low Stock Item",
        description="low stock",
        price=Decimal("10.00"),
        stock=1,
        is_active=True,
        is_approved=True,
        approval_status="Approved",
        orbit_int=True,
    )

    Product.objects.create(
        seller=seller,
        category=category,
        name="Out of Stock Item",
        description="out",
        price=Decimal("10.00"),
        stock=0,
        is_active=True,
        is_approved=True,
        approval_status="Approved",
        orbit_int=True,
    )

    client.force_login(seller)
    response = client.get(reverse("sellerInventory"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Low Stock" in content
    assert "Out of Stock" in content


@pytest.mark.django_db
def test_seller_can_create_product(client, seller, category):
    client.force_login(seller)

    response = client.post(
        reverse("createProd"),
        {
            "name": "New Seller Product",
            "description": "Created by seller",
            "price": "49.99",
            "stock": "4",
            "category": category.pk,
        },
    )

    assert response.status_code == 302

    product = Product.objects.get(name="New Seller Product")
    assert product.seller == seller
    assert product.is_approved is False
    assert product.approval_status == "Pending"
    assert product.orbit_int is True
    assert product.redirect_int is None
    assert product.deleted_at is None


@pytest.mark.django_db
def test_seller_can_update_stock_immediately(client, seller, seller_product):
    client.force_login(seller)

    response = client.post(
        reverse("editProd", args=[seller_product.pk]),
        {
            "name": seller_product.name,
            "description": seller_product.description,
            "price": str(seller_product.price),
            "stock": "7",
            "category": seller_product.category.pk,
            "orbit_int": "true",
        },
    )

    assert response.status_code == 302

    seller_product.refresh_from_db()
    assert seller_product.stock == 7


@pytest.mark.django_db
def test_seller_edit_name_creates_pending_replacement_product(client, seller, seller_product):
    client.force_login(seller)

    response = client.post(
        reverse("editProd", args=[seller_product.pk]),
        {
            "name": "Updated Seller Item",
            "description": seller_product.description,
            "price": str(seller_product.price),
            "stock": str(seller_product.stock),
            "category": seller_product.category.pk,
            "orbit_int": "true",
        },
    )

    assert response.status_code == 302

    seller_product.refresh_from_db()
    assert seller_product.redirect_int is not None
    assert seller_product.orbit_int is False

    new_product = seller_product.redirect_int
    assert new_product.name == "Updated Seller Item"
    assert new_product.is_approved is False
    assert new_product.approval_status == "Pending"
    assert new_product.seller == seller


@pytest.mark.django_db
def test_seller_can_delist_product(client, seller, seller_product):
    client.force_login(seller)

    response = client.post(reverse("delistProd", args=[seller_product.pk]))

    assert response.status_code == 302
    seller_product.refresh_from_db()
    assert seller_product.deleted_at is not None


@pytest.mark.django_db
def test_delisted_product_is_not_shown_in_seller_inventory(client, seller, seller_product):
    seller_product.deleted_at = seller_product.deleted_at or __import__("django.utils.timezone").utils.timezone.now()
    seller_product.save(update_fields=["deleted_at"])

    client.force_login(seller)
    response = client.get(reverse("sellerInventory"))

    assert "Seller Item" not in response.content.decode()


@pytest.mark.django_db
def test_seller_storefront_only_shows_buyer_visible_products(client, seller, category):
    Product.objects.create(
        seller=seller,
        category=category,
        name="Visible Product",
        description="ok",
        price=Decimal("10.00"),
        stock=3,
        is_active=True,
        is_approved=True,
        approval_status="Approved",
        orbit_int=True,
        redirect_int=None,
        deleted_at=None,
    )

    Product.objects.create(
        seller=seller,
        category=category,
        name="Hidden Product",
        description="hidden",
        price=Decimal("10.00"),
        stock=3,
        is_active=False,
        is_approved=True,
        approval_status="Approved",
        orbit_int=True,
        redirect_int=None,
        deleted_at=None,
    )

    response = client.get(reverse("sellerProducts", args=[seller.pk]))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Visible Product" in content
    assert "Hidden Product" not in content


@pytest.mark.django_db
def test_pending_product_is_not_shown_in_seller_storefront(client, seller, pending_product):
    response = client.get(reverse("sellerProducts", args=[seller.pk]))
    content = response.content.decode()

    assert response.status_code == 200
    assert "Pending Item" not in content


@pytest.mark.django_db
def test_seller_can_view_payout_page(client, seller):
    client.force_login(seller)
    response = client.get(reverse("sellerPayouts"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_seller_payout_page_only_shows_own_payouts(client, seller, category):
    other_seller = User.objects.create_user(
        username="seller2",
        password="testpass123",
        role="seller",
        email="seller2@test.com",
    )

    order_owner = User.objects.create_user(
        username="buyerx",
        password="testpass123",
        role="buyer",
        email="buyerx@test.com",
    )

    seller_product = Product.objects.create(
        seller=seller,
        category=category,
        name="My Sold Product",
        description="mine",
        price=Decimal("12.00"),
        stock=5,
        is_active=True,
        is_approved=True,
        approval_status="Approved",
        orbit_int=True,
    )

    other_product = Product.objects.create(
        seller=other_seller,
        category=category,
        name="Other Sold Product",
        description="other",
        price=Decimal("15.00"),
        stock=5,
        is_active=True,
        is_approved=True,
        approval_status="Approved",
        orbit_int=True,
    )

    from shop.models import Address, Order, OrderItem

    address = Address.objects.create(
        user=order_owner,
        full_name="Buyer Example",
        street="1 Main",
        city="Town",
        state="MS",
        zipcode="12345",
        country="USA",
    )

    order = Order.objects.create(
        buyer=order_owner,
        shipping_address=address,
        subtotal=Decimal("27.00"),
        total=Decimal("27.00"),
    )

    my_item = OrderItem.objects.create(order=order,product=seller_product,seller=seller,quantity=1,price_at_purchase=Decimal("12.00"),status="Completed",)

    other_item = OrderItem.objects.create(order=order,product=other_product,seller=other_seller,quantity=1,price_at_purchase=Decimal("15.00"),status="Completed",)

    Payout.objects.create(seller=seller,order_item=my_item,amount=Decimal("12.00"),status="Paid",)

    Payout.objects.create(seller=other_seller,order_item=other_item,amount=Decimal("15.00"),status="Paid",)

    client.force_login(seller)
    response = client.get(reverse("sellerPayouts"))
    content = response.content.decode()

    assert response.status_code == 200
    assert "My Sold Product" in content
    assert "Other Sold Product" not in content

