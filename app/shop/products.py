from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from models import Product
from serializers import ProductSerializer, ProductModerateSerializer
from permissions import IsSeller, IsAdmin
#This may be toooooo many includes.. need to figure out how to shorten this down

class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    def get_queryset(self):
        user = self.request.user #grabs current user 
        if not user.is_authenticated: #if user is not logged in
            qs = Product.objects.filter(is_approved=True) #if not logged in, user can still see approved catalog
        else: 
            role = getattr(user, "role", None) #get user role
            if role == "admin": #admin can see ALL products
                return Product.objects.all()
            elif role == "seller":
            #query string, pulls only seller products (approved or not), and general approved products from catalog
                return Product.objects.filter(Q(is_approved=True) | Q(seller=user))
            else: 
                #buyers role, only approved prods
                qs = Product.objects.filter (is_approved=True)
        
        #filters added in query 
        seller = self.request.GET.get("seller")
        if seller:
         qs = qs.filter(seller__username__iexact=seller)
        #find products that have same username
        
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category__name__iexact=category)
       
        minPrice = self.request.GET.get("minPrice")
        if minPrice: 
            qs=qs.filter(price_gte=minPrice)

        maxPrice = self.request.GET.get("maxPrice")
        if maxPrice: 
            qs=qs.filter(price_lte=maxPrice)

        return qs

    def get_permissions(self):
        #anyone can read product details
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        #admins only actions
        if getattr(self, "action", None) == "moderate":
            return [IsAuthenticated(), IsAdmin()]
        #sellers can edit but must be the owner of their product
        return [IsAuthenticated(), IsSeller()]

#creating a new product, called after post
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user, #prod will go to specific seller
            is_approved=False, #unapproved 
            approval_status="Pending", #pending approval
        )


    
    @action(detail=True, methods=["post"])
    #endpoint per product
    def moderate(self, request, pk=None):
        #pk is product id
        product = self.get_object()
        serializer = ProductModerateSerializer(product, data=request.data, partial=True)
        #update product with new data
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data.get("approval_status", product.approval_status)
        #gives new approval status if updated, else stay the same
        if new_status == "Approved":
            serializer.save(is_approved=True, approval_status="Approved")
        elif new_status == "Rejected":
            serializer.save(is_approved=False, approval_status="Rejected")
        else:
            serializer.save(is_approved=False, approval_status="Pending")

        return Response(
            {"id": product.id, "is_approved": product.is_approved, "approval_status": product.approval_status},
            status=status.HTTP_200_OK,
        )