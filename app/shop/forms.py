from django import forms
from .models import Product # Assuming you have a model named Article

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields =  fields = [
            "seller",
            "category",  
            "name",
            "description",
            "price",
            "stock",
            "approval_status",
        ]
       