from django.shortcuts import render, redirect
from rest_framework import generics, permissions
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class accountView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


@login_required(login_url="login")
@never_cache
def account(request):
    if request.user.role == "seller":
        return render(request, "generic/seller-account.html")
    elif request.user.role == "admin":
        return render(request, "generic/admin-account.html")
    return render(request, "generic/account.html")


@never_cache
def loginpg(request):
    errors = {}

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            role = getattr(user, "role", None)
            if role == "seller":
                return redirect("sellerInventory")
            elif role == "admin":
                return redirect("adminModeration")
            else:
                return redirect("home")
        else:
            errors["login"] = "Invalid username or password."

    response = render(request, "generic/login.html", {"errors": errors})
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response


@never_cache
def logoutpg(request):
    logout(request)
    response = render(request, "generic/logout.html")
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    response.delete_cookie("access")
    response.delete_cookie("refresh")
    return response

@never_cache
def register(request):
    errors = {}
    data = {}
    if request.method == "POST":
        data = {
            "username": request.POST.get("username", ""),
            "first_name": request.POST.get("first_name", ""),
            "last_name": request.POST.get("last_name", ""),
            "email": request.POST.get("email", ""),
            "role": request.POST.get("role", "buyer"),
            "password": request.POST.get("password", ""),
            "pswrdAgain": request.POST.get("pswrdAgain", ""),
        }

        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():
            user = serializer.save()
            auth_login(request, user)

            if user.role == "seller":
                return redirect("sellerInventory")
            elif user.role == "admin":
                return redirect("adminModeration")
            else:
                return redirect("home")

        print("REGISTER ERRORS:", serializer.errors)
        errors = serializer.errors

    response = render(request, "generic/register.html", {"errors": errors, "data": data})
    response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response["Pragma"] = "no-cache"
    response["Expires"] = "0"
    return response