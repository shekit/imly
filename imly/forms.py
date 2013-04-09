from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from imly.models import Store, Product, Category, UserProfile#, GiveTip
from django.core.mail import send_mail
import os

class MyCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        html = super(MyCheckboxSelectMultiple, self).render(name, value, attrs, choices)

        return mark_safe(html.replace('<ul>', '<ul class="inline">'))

class StoreForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        super(StoreForm,self).__init__(*args,**kwargs)
        self.fields["delivery_areas"].help_text = "Where all can you deliver? Select all that apply"
    
    class Meta:
        model = Store
        exclude = ["slug","owner","categories", "date_created","date_updated","tags", "is_featured","is_approved"]
        fields = ("name", "tagline", "description", "delivery_areas")
        widgets = {
            "delivery_areas": MyCheckboxSelectMultiple(),
        }
        
class ProductForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        super(ProductForm,self).__init__(*args,**kwargs)
        self.fields["category"].queryset = Category.objects.exclude(super_category=None)
        self.fields["tags"].help_text = "Select all that apply"
        self.fields["_unit_price"].label = "Price"
        self.fields["lead_time"].label = "Delivery Time"
        self.fields["image"].label = "Product Image"

    
    class Meta:
        model = Product
        exclude = ["slug", "date_created", "store", "is_featured", "is_bestseller", "tax_included", "tax_class", "currency"]
        fields = ("name", "_unit_price", "capacity_per_month","items_in_stock","description","lead_time","category","image","tags")
        widgets = {
            "tags": MyCheckboxSelectMultiple(),
        }
        
class OrderItemForm(forms.Form):
    quantity = forms.IntegerField(initial=1, min_value=1, max_value=50)


class UserProfileForm(forms.ModelForm):
    
    def __init_(self,*args,**kwargs):
        super(UserProfileForm,self).__init__(*args,**kwargs)
        self.fields["avatar"].label = "Profile Image"
    class Meta:
        model = UserProfile
        fields = ("first_name","last_name","about_me","avatar")
        exclude = ["user","avatar_thumbnail","avatar_thumbnail_mini"]

    '''def get_image(self):
        if not self.avatar:
            self.avatar = os.path.abspath('/imly_project/media/images/image.jpg')
            return self.avatar'''
"""    
class GiveTipForm(forms.ModelForm):
    
    class Meta:
        model = GiveTip
        
    def send_email(self):
        send_mail("Feedback Submitted","Feedback by %s:  %s" % (self.instance.name, self.instance.message), self.instance.email, ["imlyfood@gmail.com"], fail_silently=False)
"""