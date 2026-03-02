from django.urls import path,include
from .views import (home, catalog, adminModeration, brandResults, billing, orderConf, orders, addresses, returns,  returnReq, )
from rest_framework.routers import DefaultRouter
from .products import ProductViewSet
#auto generates a root URL API endpoint page
#handles get, post, patch, delete
router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="products")


urlpatterns = [
    path("home/", home, name="home"),
    path("", include(router.urls)),
    path("brands/<str:brand>/", brandResults, name="brandResults"),
    path("admin/moderation/", adminModeration, name="adminModeration"),
    path("billing/", billing, name="billing"),
    path("orderConf/", orderConf, name="orderConf"),
    path("orders/", orders, name="orders"),
    path("addresses/", addresses, name="addresses"),
    path("returns/", returns, name="returns"),
    path("returns/request/", returnReq, name="returnReq"),
    path("catalog/", catalog, name="catalog"),
]