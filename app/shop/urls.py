from django.urls import path
from .views import products_list

urlpatterns = [
    path("products/", products_list, name="product_list_api"),
]