import base64
import json
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Product
from .serializers import ProductSerializer

@api_view(["GET"])
@permission_classes([AllowAny])
def products_list(request):
    qs = Product.objects.filter(approval_status="Approved").order_by("id")

    q = request.query_params.get("q")
    if q:
        qs = qs.filter(name__icontains=q)

    return Response(ProductSerializer(qs, many=True).data)




