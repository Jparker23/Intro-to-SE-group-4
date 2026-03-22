from django.urls import path,include
from .views import (home, catalog, comparison, seller_admin_catalog, set_default_address, delete_address, set_default_payment, delete_payment, prod_details, buyer_only_catalog, adminModeration, sellerInventory, sellerProducts,  brandResults, billing, orderConf, orders, addresses, returns,  returnReq, createProd, checkout, editProd, delistProd)
from rest_framework.routers import DefaultRouter
from .products import ProductViewSet
#auto generates root URL API endpoint pages
#handles get, post, patch, delete
router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="products")



urlpatterns = [
    path("home/", home, name="home"),
    path("", include(router.urls)),
    path("brands/<str:brand>/", brandResults, name="brandResults"),
    path("admin/moderation/", adminModeration, name="adminModeration"),
    path("orderConf/", orderConf, name="orderConf"),
    path("account/orders/", orders, name="orders"),
    path("account/addresses/", addresses, name="addresses"),
    path("account/billing/", billing, name="billing"),
    path("account/addresses/default/<int:address_id>/", set_default_address, name="set_default_address"),
    path("account/addresses/delete/<int:address_id>/", delete_address, name="delete_address"),
    path("account/billing/default/<int:payment_id>/", set_default_payment, name="set_default_payment"),
    path("account/billing/delete/<int:payment_id>/", delete_payment, name="delete_payment"),
    path("account/returns/", returns, name="returns"),
    path("account/returns/request/", returnReq, name="returnReq"),

    #admin and seller catalog
    path("seller/catalog/", sellerInventory, name="sellerInventory"),
    path("catalog/", buyer_only_catalog, name="catalog"),
    path("seller/<int:pk>/products", sellerProducts, name="sellerProducts"),
    path("inventory/", sellerInventory, name="sellerInventory"),
    path("seller/products/new/", createProd, name="createProd"),
    path("compare/", comparison, name="compare"),
    path("product/<int:pk>/", prod_details, name="prod_details"),
    path("checkout/", checkout, name="checkout"),
    path("seller/products/<int:pk>/edit/", editProd, name="editProd"),
    path("seller/products/<int:pk>/delist/", delistProd, name="delistProd"),
]

