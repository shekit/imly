from django import forms
from imly.models import Store, Product, Category

class StoreForm(forms.ModelForm):
    
    class Meta:
        model = Store
        exclude = ["slug","owner","date_created","date_updated", "is_featured","is_approved"]
        
class ProductForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        super(ProductForm,self).__init__(*args,**kwargs)
        self.fields["category"].queryset = Category.objects.exclude(super_category=None)
    
    class Meta:
        model = Product
        exclude = ["slug", "date_created", "store", "is_featured", "is_bestseller", "tax_included", "currency"]
        widgets = {
            "tags": forms.CheckboxSelectMultiple,
        }
        
class OrderItemForm(forms.Form):
    quantity = forms.IntegerField(initial=1, min_value=1, max_value=50)