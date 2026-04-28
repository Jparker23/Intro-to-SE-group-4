from django.urls import path
from . import views

urlpatterns = [
    
    path("register/", views.register, name="register"),
    path("account/", views.account, name="account"),
    path("login/", views.loginpg, name="login"),
    path("logout/", views.logoutpg, name="logout"),
    path("api/auth/register/", views.RegisterView.as_view(), name="api-register"),
    path("pending-approval/", views.pending_approval, name="pending_approval"),

]