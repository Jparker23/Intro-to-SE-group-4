from django import forms
from .models import Product 

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields =  fields = [
            "category",  
            "name",
            "description",
            "price",
            "stock",
            "photo"
        ]
       