from rest_framework.permissions import BasePermission
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSellerAndOwnerOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and getattr(request.user, "role", None) == "seller"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.seller_id == request.user.id
