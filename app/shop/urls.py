from django.urls import path,include
from .views import (home, comparison, seller_notifications, mark_notification_read,seller_notifications_rss,sellerInventory, unhide_review, submit_review, hide_review, sellerPayouts, adminCatalog, set_default_address, delete_address, set_default_payment, delete_payment, prod_details, buyer_only_catalog, adminModeration, sellerInventory, sellerProducts,  brandResults, billing, orderConf, orders, addresses, returns,  returnReq, createProd, checkout, editProd, delistProd, sellerOrders, approve_product, approve_return, deny_product, deny_return, approve_user, deny_user, markShipped)
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
    path("admin/catalog/", adminCatalog, name="adminCatalog"),
    path("catalog/", buyer_only_catalog, name="catalog"),
    path("seller/<int:pk>/products", sellerProducts, name="sellerProducts"),
    path("inventory/", sellerInventory, name="sellerInventory"),
    path("seller/products/new/", createProd, name="createProd"),
    path("compare/", comparison, name="compare"),
    path("product/<int:pk>/", prod_details, name="prod_details"),
    path("checkout/", checkout, name="checkout"),
    path("seller/products/<int:pk>/edit/", editProd, name="editProd"),
    path("seller/products/<int:pk>/delist/", delistProd, name="delistProd"),
    path("seller/orders/", sellerOrders, name="sellerOrders"),
    path("seller/payouts/", sellerPayouts, name="sellerPayouts"),
    path("admin/products/<int:pk>/approve/", approve_product, name="approve_product"),
    path("admin/products/<int:pk>/deny/", deny_product, name="deny_product"),
    path("admin/returns/<int:pk>/approve/", approve_return, name="approve_return"),
    path("admin/returns/<int:pk>/deny/", deny_return, name="deny_return"),
    path("admin/users/<int:pk>/approve/", approve_user, name="approve_user"),
    path("admin/users/<int:pk>/deny/", deny_user, name="deny_user"),
    path("products/<int:product_id>/review/", submit_review, name="submit_review"),
    path("reviews/<int:review_id>/hide/", hide_review, name="hide_review"),
    path("reviews/<int:review_id>/unhide/", unhide_review, name="unhide_review"),
    path("seller/notifications/", seller_notifications, name="seller_notifications"),
    path("seller/notifications/rss/", seller_notifications_rss, name="seller_notifications_rss"),
    path("seller/notifications/<int:notification_id>/read/", mark_notification_read, name="mark_notification_read"),
    path("seller/orders/<int:pk>/ship/", markShipped, name="markShipped"),
   
]
