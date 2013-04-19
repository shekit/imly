from django import forms
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from imly.models import Store, Product, Category, UserProfile#, GiveTip
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
import os

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, Div
from crispy_forms.bootstrap import PrependedText

class MyCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        html = super(MyCheckboxSelectMultiple, self).render(name, value, attrs, choices)

        return mark_safe(html.replace('<ul>', '<ul class="inline">'))

class StoreForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        super(StoreForm,self).__init__(*args,**kwargs)
        self.fields["provide_delivery"].label = "Provide Delivery?"
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "",
                "name",
                "tagline",
                PrependedText("store_contact_number", "+91", placeholder="Mobile Number"),
                "description"
                ),
            Fieldset(
                "",
                "pick_up",
                Div(
                    "pick_up_address",
                    Field("pick_up_location",placeholder="e.g Breach Candy etc"),
                    css_class="pick_up"
                ),
                "provide_delivery",
                Div(
                    "delivery_areas",
                    css_class="delivery_areas"
                )
                ),
            Fieldset(
                "",
                "facebook_link",
                "twitter_link",
            ),
        )

        self.fields["delivery_areas"].help_text = "Where all can you deliver? Select all that apply"

    def clean_store_contact_number(self):
        contact = self.cleaned_data['store_contact_number']
        if len(contact) != 10:
            raise forms.ValidationError("Mobile number should be 10")
        return contact
    
    def clean(self):
        cleaned_data = super(StoreForm, self).clean()
        pick_up_address = cleaned_data.get("pick_up_address")
        delivery_areas = cleaned_data.get("delivery_areas")
        
        if not pick_up_address and not delivery_areas:
            msg=u"You must either define a pick up point or a delivery area(s)"
            self._errors["pick_up"] = self.error_class([msg])
            
            del cleaned_data["pick_up_address"]
            del cleaned_data["delivery_areas"]
        
        return cleaned_data
        
    class Meta:
        model = Store
        exclude = ["slug","owner","categories", "date_created","date_updated","tags", "is_featured","is_approved"]
        fields = ("name", "tagline", "store_contact_number","description","pick_up","pick_up_address","pick_up_location","provide_delivery", "delivery_areas", "facebook_link", "twitter_link")
        widgets = {
            "delivery_areas": MyCheckboxSelectMultiple(),
        }
        
        
"""    def __init__(self,*args,**kwargs):
        super(StoreForm,self).__init__(*args,**kwargs)
        self.fields["delivery_areas"].help_text = "Where all can you deliver? Select all that apply"
    
    class Meta:
        model = Store
        exclude = ["slug","owner","categories", "date_created","date_updated","tags", "is_featured","is_approved"]
        fields = ("name", "tagline", "store_contact_number","description", "delivery_areas")
        widgets = {
            "delivery_areas": MyCheckboxSelectMultiple(),
        }"""

"""class StoreNotice(forms.ModelForm):
        
    class Meta:
        model = Store
        exclude = ["name", "tagline", "store_contact_number","description", "delivery_areas", "slug","owner","categories", "date_created","date_updated","tags", "is_featured","is_approved"]
        fields = ("store_notice",)"""
        
class ProductForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        super(ProductForm,self).__init__(*args,**kwargs)
        self.fields["category"].queryset = Category.objects.exclude(super_category=None)
        self.fields["tags"].help_text = "Select all that apply"
        self.fields["_unit_price"].label = "Price"
        self.fields["quantity_per_item"].label = "Quantity"
        self.fields["quantity_by_price"].label = "Unit"
        self.fields["lead_time"].label = "Delivery Time"
        self.fields["lead_time_unit"].label = "Unit"
        self.fields["image"].label = "Product Image"
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "",
                "name",
                Div(
                    Div(
                        PrependedText("_unit_price","INR", css_class="input-mini"),
                        css_class="span2"),
                    Div(
                        PrependedText("quantity_per_item", "per",css_class="input-mini"),
                        css_class="span2"),
                    Div(
                        Field("quantity_by_price",css_class="input-small"),
                        css_class="span2"),
                    Div(
                        css_class="span6"),
                    css_class="row-fluid inline_form_field"),
                "capacity_per_month",
                "description",
                Div(
                    Div(
                        Field("lead_time",css_class="input-small"),
                        css_class="span2"),
                    Div(
                        Field("lead_time_unit", css_class="input-small"),
                        css_class="span2"),
                    Div(
                        css_class="span8"),
                    css_class="row-fluid"),
                "category",
                "image",
                "tags",
            ),
        )

    
    class Meta:
        model = Product
        exclude = ["slug", "date_created", "store", "is_featured", "is_bestseller", "tax_included", "tax_class", "currency"]
        fields = ("name", "_unit_price","quantity_per_item","quantity_by_price", "capacity_per_month","description","lead_time","lead_time_unit","category","image","tags")
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