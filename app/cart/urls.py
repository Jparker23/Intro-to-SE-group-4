from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_details, name='cart_details'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path("update/<int:product_id>/", views.update_cart_item, name="update_cart_item"),
]