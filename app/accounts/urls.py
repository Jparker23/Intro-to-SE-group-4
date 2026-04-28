from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    
    path("register/", views.register, name="register"),
    path("account/", views.account, name="account"),
    path("login/", views.loginpg, name="login"),
    path("logout/", views.logoutpg, name="logout"),
    path("api/auth/register/", views.RegisterView.as_view(), name="api-register"),
    path("pending-approval/", views.pending_approval, name="pending_approval"),
    path("password-reset/", auth_views.PasswordResetView.as_view(
        template_name='generic/password-reset-form.html',
        email_template_name='generic/password-reset-email.html',
        success_url='/api/auth/password-reset/done/',), name='password-reset'),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name='generic/password-reset-done.html'), name='password-reset-done'),
    path("password-reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name='generic/password-reset-confirm.html',
        success_url='/api/auth/password-reset/complete/',), name='password-reset-confirm'),
    path("password-reset/complete/", auth_views.PasswordResetCompleteView.as_view(
        template_name='generic/password-reset-complete.html',), name='password-reset-complete'),
]