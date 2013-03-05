from django import forms
from imly.models import Store, Product

class StoreForm(forms.ModelForm):
    
    class Meta:
        model = Store
        exclude = ["slug","owner","date_created","date_updated", "is_featured","is_approved"]
        
class ProductForm(forms.ModelForm):
    
    class Meta:
        model = Product
        exclude = ["slug", "date_created", "store", "is_featured", "is_bestseller"]
        
class OrderItemForm(forms.Form):
    quantity = forms.IntegerField(initial=1, min_value=1, max_value=50)