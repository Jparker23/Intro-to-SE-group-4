from django.shortcuts import render, redirect, get_object_or_404

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer
from .forms import ProductForm
from rest_framework.permissions import SAFE_METHODS
from .permissions import IsSellerAndOwnerOrReadOnly
from rest_framework.viewsets import ModelViewSet


@api_view(["GET"])
@permission_classes([AllowAny])
def products_list(request):
    qs = Product.objects.filter(approval_status="Approved").order_by("id")

    q = request.query_params.get("q")
    if q:
        qs = qs.filter(name__icontains=q)

    return Response(ProductSerializer(qs, many=True).data)



def create_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm()

    return render(request, "shop/product_form.html", {"form": form})


def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect("product_list")
    else:
        form = ProductForm(instance=product)

    return render(request, "shop/product_form.html", {"form": form})

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        # Anyone can browse products (GET/HEAD/OPTIONS)
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        # Only sellers can POST/PUT/PATCH/DELETE
        return [IsSellerAndOwnerOrReadOnly()]

    def perform_create(self, serializer):
        # Force seller = logged-in seller (prevents spoofing)
        serializer.save(seller=self.request.user)