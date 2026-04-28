from django.shortcuts import render, redirect
from typing import cast
from rest_framework import generics, permissions
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .serializers import RegisterSerializer, UserSerializer
from accounts.models import User
from shop.utils import create_audit_log



class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class accountView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

@never_cache
@login_required(login_url="login")
def account(request):
    user = cast(User, request.user)

    if user.role == "seller":
        return render(request, "generic/seller-account.html")
    elif user.role == "admin":
        return render(request, "generic/admin-account.html")
    return render(request, "generic/account.html")


@never_cache
def loginpg(request):
    errors = {}

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        auth_user = authenticate(request, username=username, password=password)

        if auth_user is not None:
            user = cast(User, auth_user)

            if not user.is_active:
                errors["login"] = "This account is inactive."
                create_audit_log( request, action="LOGIN_BLOCKED_INACTIVE", details=f"Inactive account login blocked for username={username}", user=user, )
            elif not user.is_approved:
                errors["login"] = "This account is pending admin approval."
                create_audit_log( request, action="LOGIN_BLOCKED_UNAPPROVED", details=f"Unapproved account login blocked for username={username}", user=user,)
            else:
                auth_login(request, user)

                create_audit_log(request, action="LOGIN_SUCCESS", details=f"Successful login for username={user.username}", user=user,)

                if user.role == "seller":
                    return redirect("sellerInventory")
                elif user.role == "admin":
                    return redirect("adminModeration")
                else:
                    return redirect("home")
        else:
            errors["login"] = "Invalid username or password."
            create_audit_log(request, action="LOGIN_FAILED", details=f"Failed login attempt for username={username}",)

    response = render(request, "generic/login.html", {"errors": errors})
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


@never_cache
def logoutpg(request):
    if request.user.is_authenticated:
        create_audit_log( request, action="LOGOUT", details=f"User {request.user.username} logged out", )

    logout(request)
    request.session.flush()
    response = redirect("login")
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    response.delete_cookie("sessionid")
    response.delete_cookie("csrftoken")
    response.delete_cookie("access")
    response.delete_cookie("refresh")
    return response


@never_cache
def register(request):
    errors = {}
    data = {}

    if request.method == "POST":
        data = {
            "username": request.POST.get("username", "").strip(),
            "first_name": request.POST.get("first_name", "").strip(),
            "last_name": request.POST.get("last_name", "").strip(),
            "email": request.POST.get("email", "").strip(),
            "role": request.POST.get("role", "buyer"),
            "password": request.POST.get("password", ""),
            "pswrdAgain": request.POST.get("pswrdAgain", ""),
        }

        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():
            created_user = serializer.save()
            user = cast(User, created_user)

            if user.role == "buyer":
                user.is_approved = False
                user.save(update_fields=["is_approved"])

                create_audit_log( request, action="REGISTER_BUYER_AUTO_APPROVED", details=f"Buyer account created for username={user.username}", target_type="User", target_id=user.pk, user=user,)

                return redirect("pending_approval")

            user.is_approved = False
            user.save(update_fields=["is_approved"])

            create_audit_log( request, action="REGISTER_ACCOUNT_PENDING_APPROVAL", details=f"Account created pending approval for username={user.username}, role={user.role}", target_type="User", target_id=user.pk, user=user, )

            return redirect("pending_approval")

        create_audit_log( request, action="REGISTER_FAILED", details=f"Registration failed for username={data.get('username', '')}, email={data.get('email', '')}, errors={serializer.errors}",)
        errors = serializer.errors

    response = render(request, "generic/register.html", {"errors": errors, "data": data})
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response

@never_cache
def pending_approval(request):
    response = render(request, "generic/pending-approval.html")
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response