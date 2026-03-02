from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        #everyone can view and see products
        if request.method in SAFE_METHODS:
            return True
        #user has to be logged in and be a seller to interact (edit, delete, post) a product
        return bool (request.user and request.user.is_authenticated and getattr(request.user, "role", None) == "seller")
    #When a specific product needs to be edited or deleted:
    def has_object_permission(self, request, view, obj):
        #any user can see product details
        if request.method in SAFE_METHODS:
            return True
        #checks user is logged in, has a role, and that their product matches the correct seller
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", None) and obj.seller == request.user)


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        #user must be logged in and have a admin role
        return request.user.is_authenticated and getattr(request.user, "role", None)== "admin"
