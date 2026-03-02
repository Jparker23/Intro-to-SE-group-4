from rest_framework import serializers #bridge between DB and front end
from .models import Product
#https://www.django-rest-framework.org/api-guide/serializers/#declaring-serializers

class ProductSerializer(serializers.ModelSerializer):
    seller_email = serializers.EmailField(source="seller.email", read_only=True)
#finds seller FK from product, then finds sellers email, connects it to a sellers product
    class Meta:
        model = Product
        fields = ["id","name","description","price","stock","approval_status","seller_email",]
        #status and email cant be changed
        read_only_fields = ["is_approved", "approval_status", "seller_email"]
#this acts more like a admin control, so admins can update and change approval status 
class ProductModerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("approval_status", "is_approved")