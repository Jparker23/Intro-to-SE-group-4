from django.shortcuts import render, redirect
from rest_framework import generics, permissions
from django.contrib.auth import authenticate, login as auth_login, logout
from .serializers import RegisterSerializer, UserSerializer

#POST request handler, used for user registration
class RegisterView(generics.CreateAPIView):
    #anyone can get to the registration endpoint
    permission_classes = [permissions.AllowAny]
    #validate data/create user object
    serializer_class = RegisterSerializer

#used for account page, GET request handler
class accountView(generics.RetrieveAPIView):
    #requires user to be logged in
    permission_classes = [permissions.IsAuthenticated]
    #gets users id, username, email, and role
    serializer_class = UserSerializer

    def get_object(self):
        #get whos ever logged in, attached to account
        return self.request.user
    
def account(request):
    return render(request, "generic/account.html")
  
def loginpg(request):
    errors = {}

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("home")
        else:
            errors["login"] = "Invalid username or password."

    return render(request, "generic/login.html", {"errors": errors})

def logoutpg(request):
    logout(request)
    return render(request, "generic/logout.html")

def register(request):
    errors = {}
    data = {}
    if request.method == "POST":
        data = {"username": request.POST.get("username", ""),
                "first_name": request.POST.get("first_name", ""),
                "last_name": request.POST.get("last_name", ""),
                "email": request.POST.get("email", ""),
                "role": request.POST.get("role", "buyer"),
                "password": request.POST.get("password", ""),
                "pswrdAgain": request.POST.get("pswrdAgain", ""),
        }
       
        #seralizes collected data
        serializer = RegisterSerializer(data=data)
        #validation of data
        if serializer.is_valid():
            #if its valid, the data is saved, a user will then be created
            user = serializer.save()
            #new user logs in immediately
            auth_login(request, user) 
            return redirect("home")
        print("REGISTER ERRORS:", serializer.errors)
        errors = serializer.errors
    return render(request, "generic/register.html", {"errors": errors, "data": data})