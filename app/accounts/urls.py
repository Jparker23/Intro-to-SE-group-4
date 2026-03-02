from django.urls import path
from .views import register, account, loginpg, logoutpg

urlpatterns = [
    
    path("register/", register, name="register"),
    path("account/", account, name="account"),
    path("login/", loginpg, name="login"),
    path("logout/", logoutpg, name="logout"),

]