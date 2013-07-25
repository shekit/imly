from django import forms
from django.forms.models import inlineformset_factory
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from imly.models import Store, Product, Category, UserProfile, ChefTip,DeliveryLocation, Recipe, RecipeStep, Ingredient
from imly.fields import GroupedModelChoiceField
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.db.models import Count
import os
import re
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Submit, Div, HTML
from crispy_forms.bootstrap import PrependedText
from crispy_forms.layout import Field

class FileField(Field):
    template = "bootstrap/layout/file_field.html"
    
class MyCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        html = super(MyCheckboxSelectMultiple, self).render(name, value, attrs, choices)

        return mark_safe(html.replace('<ul>', '<ul class="inline">'))

class StoreForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        super(StoreForm,self).__init__(*args,**kwargs)
        self.fields["pick_up"].label = "Do you provide pick up from the above address?"
        self.fields["provide_delivery"].label = "Provide Delivery?"
        self.fields["pick_up_address"].label = "Your Address"
        self.fields["pick_up_location"].label = "Area/Locality"
        self.fields["pick_up_landmark"].label = "Landmark Nearby"
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "Shop Details",
                "name",
                "logo",
                "cover_photo",
                "tagline",
                PrependedText("store_contact_number", "+91", placeholder="Mobile Number"),
                Field("description",rows="5"),
                ),
            Fieldset(
                "Social Media Info",
                "facebook_link",
                "twitter_link",
            ),
            Fieldset(
                "Delivery/Pick-Up Details",
                Div(
                    HTML("<p style='font-weight:400; font-size:14px;'>We need your address for our <span class='orange'>location based searching.</span><br>It's safe with us and won't be displayed.</p><br>"),
                    Field("pick_up_address",rows="4", placeholder="Only shared with confirmed buyers in case of pick-up. Not displayed on imly :)"),
                    Field("pick_up_location",placeholder="e.g Breach Candy etc"),
                    Field("pick_up_landmark"),
                    css_class="pick_up"
                ),
                "pick_up",
                "provide_delivery",

                ),
        )

        #self.fields["delivery_areas"].help_text = "Where all can you deliver? Select all that apply"

    def clean_store_contact_number(self):
        contact = self.cleaned_data['store_contact_number']
        if len(contact) != 10 or not re.match('^\d+$',contact):
            raise forms.ValidationError("Mobile number must be 10 digits & number.")
        return contact
    
    def clean_name(self):
        if Store.objects.filter(name=self.cleaned_data['name']).exclude(pk=self.instance.pk).count() > 0:
            raise ValidationError("A store with this name already exists. Please choose another name")
        return self.cleaned_data["name"]
    
    def clean(self):
        cleaned_data = super(StoreForm, self).clean()
        pick_up_address = cleaned_data.get("pick_up_address")
        #delivery_areas = cleaned_data.get("delivery_areas")
        pick_up_checkbox = cleaned_data.get("pick_up")
        delivery_checkbox = cleaned_data.get("provide_delivery")
        pick_up_location = cleaned_data.get("pick_up_location")

                        
        if pick_up_checkbox and not (pick_up_address and pick_up_location):
            msg = u"Please enter your complete pick up point details above"
            self._errors["pick_up"] = self.error_class([msg])
        
        #elif (pick_up_address or pick_up_location) and not pick_up_checkbox:
         #   msg = u"You have entered pick up details. Please check this box or remove the details"
          #  self._errors["pick_up"] = self.error_class([msg])
            
        #elif delivery_checkbox and not delivery_areas:
         #   msg = u"Please select your areas of delivery"
          #  self._errors["provide_delivery"] = self.error_class([msg])
        
        #elif delivery_areas and not delivery_checkbox:
         #   msg = u"You have entered delivery details.Please check this box or uncheck the locations"
          #  self._errors["provide_delivery"] = self.error_class([msg])
            
        elif not pick_up_address and not delivery_checkbox:
            msg=u"You must either define a pick up point or a delivery area(s)"
            self._errors["pick_up"] = self.error_class([msg])
            
            del cleaned_data["pick_up_address"]
            #del cleaned_data["delivery_areas"]
            
        return cleaned_data
        
    class Meta:
        model = Store
        exclude = ["slug","owner","categories", "date_created","date_updated","tags", "is_featured","is_approved"]
        fields = ("name","logo","cover_photo", "tagline", "store_contact_number","description","pick_up","pick_up_address","pick_up_location","pick_up_landmark","provide_delivery", "facebook_link", "twitter_link")
        widgets = {
            "delivery_areas": MyCheckboxSelectMultiple(),
        }
        
class DeliveryLocationForm(forms.ModelForm):
    class Meta:
        model = DeliveryLocation
        fields = ('name', )
        
DeliveryLocationFormSet = inlineformset_factory(Store, DeliveryLocation, DeliveryLocationForm, extra=0)

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
    category = GroupedModelChoiceField(queryset=Category.objects.order_by('super_category'), group_by_field='super_category', group_label=lambda c: c.name)
    
    def __init__(self,*args,**kwargs):
        super(ProductForm,self).__init__(*args,**kwargs)
        self.fields["category"].queryset = Category.objects.exclude(super_category=None)
        self.fields["tags"].help_text = "Select all that apply"
        self.fields["_unit_price"].label = "Price"
        self.fields["quantity_per_item"].label = "Quantity"
        self.fields["quantity_by_price"].label = "Unit"
        self.fields["capacity_per_day"].label = "Capacity per day <a href='#' class='form-tips' title='How many units of this item(as defined above) can you make in a single day.'>[?]</a>"
        self.fields["lead_time"].label = "Notice Period <a href='#' class='form-tips' title='The advance notice period you need to prepare the dish and have it ready for delivery/pick-up'>[?]</a>"
        self.fields["lead_time_unit"].label = "<br>"
        self.fields["image"].label = "Product Image"
        self.fields["tags"].label = "Tags <a href='#' class='form-tips' title='Check all that apply so buyers can better search for your dish.'>[?]</a>"
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "",
                "name",
                HTML("<p style='font-weight:500; font-size:14px; color:#f05a28;'>Your minimum order :</p>"),
                Div(
                    Div(
                        PrependedText("_unit_price","INR", css_class="input-mini"),
                        css_class="span2"),
                    Div(
                        PrependedText("quantity_per_item", "for",css_class="input-mini"),
                        css_class="span2"),
                    Div(
                        Field("quantity_by_price",css_class="input-small"),
                        css_class="span2"),
                    Div(
                        css_class="span6"),
                    css_class="row-fluid inline_form_field"),
                "capacity_per_day",
                Field("description", rows="5"),
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

    def clean_name(self):
        if Product.objects.filter(name=self.cleaned_data['name'], store=self.instance.store).exclude(pk=self.instance.pk).count() > 0:
            raise ValidationError(u'You already have a product with the same name in your store.')
        return self.cleaned_data['name']

    class Meta:
        model = Product
        exclude = ["slug", "date_created", "store", "is_featured", "is_bestseller", "tax_included", "tax_class", "currency"]
        fields = ("name", "_unit_price","quantity_per_item","quantity_by_price", "capacity_per_day","description","lead_time","lead_time_unit","category","image","tags")
        widgets = {
            "tags": MyCheckboxSelectMultiple(),
        }
        
class RecipeForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(RecipeForm,self).__init__(*args,**kwargs)
        self.fields["cook_time"].label = "Cooking Time"
        self.fields["serves"].label = "No. of people this dish serves"
        self.fields["prep_time_choices"].label = "<br>"
        self.fields["cook_time_choices"].label = "<br>"
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "",
                Div(
                    Div(
                        Field("prep_time",css_class="input-small", placeholder="Time"),
                        css_class="span2"),
                    Div(
                        Field("prep_time_choices", css_class="input-small"),
                        css_class="span2"),
                    Div(
                        Field("cook_time",css_class="input-small", placeholder="Time"),
                        css_class="span2"),
                    Div(
                        Field("cook_time_choices", css_class="input-small"),
                        css_class="span2"),
                    Div(
                        css_class="span4"),
                    css_class="row-fluid"),
                Field("serves",css_class="input-mini"),
                ),
                
        )

        
    class Meta:
        model = Recipe
        exclude = ["product","store", "category", "created","updated", "chef_note", "ingredients"]
        fields = ("prep_time","prep_time_choices","cook_time", "cook_time_choices","serves")
        widgets = {
            "delivery_areas": MyCheckboxSelectMultiple(),
        }
        
class RecipeStepForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(RecipeStepForm,self).__init__(*args, **kwargs)
        self.fields["description"].label = ""
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "",
                Field("description",css_class="recipe_step_textarea",rows="3"),
            )
        )
        
    class Meta:
        model = RecipeStep
        fields = ('description', )
        exclude = ("recipe",)
        
RecipeStepFormSet = inlineformset_factory(Recipe, RecipeStep, RecipeStepForm, extra=4)
RecipeStepFormSetEdit = inlineformset_factory(Recipe, RecipeStep, RecipeStepForm, extra=0)

class RecipeIngredientForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        super(RecipeIngredientForm,self).__init__(*args,**kwargs)
        self.fields["name"].label = ""
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "",
                Div(
                        Field("name",placeholder="Ingredient"),
                        css_class="ingredient_set"),
                ),
            
        )
        
    class Meta:
        model = Ingredient
        fields = ("name",)
        exclude = ("recipe",)

        
RecipeIngredientFormSet = inlineformset_factory(Recipe, Ingredient, RecipeIngredientForm, extra=4)
RecipeIngredientFormSetEdit = inlineformset_factory(Recipe, Ingredient, RecipeIngredientForm, extra=0)
     
class OrderItemForm(forms.Form):
    quantity = forms.IntegerField(initial=1, min_value=1)
            
    """
    def __init__(self,*args,**kwargs):
        super(OrderItemForm,self).__init__(*args,**kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "",
                Field("quantity",css_class="span3"),
            ),
        )
        """

class UserProfileForm(forms.ModelForm):
    
    def __init__(self,*args,**kwargs):
        super(UserProfileForm,self).__init__(*args,**kwargs)
        self.fields["cover_profile_image"].label = "Profile Image <a href='#' class='form-tips' title='Choose a large image. Atleast 1600px wide for best results. Take inspiration from our chef profiles.'>[?]</a>"
        self.fields["word_one"].label = "Three words that best describe you"
        self.fields["word_two"].label = "<br><br>"
        self.fields["word_three"].label = "<br><br>"
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                "",
                Div(
                    Div(Field("first_name"),css_class="span4"),
                    Div(Field("last_name"),css_class="span4"),
                    Div(css_class="span4"),
                    css_class="row-fluid"),
                "cover_profile_image",
                Div(
                    Div(Field("word_one",css_class="input-small"),css_class="span2"),
                    Div(Field("word_two",css_class="input-small"),css_class="span2"),
                    Div(Field("word_three",css_class="input-small"),css_class="span2"),
                    Div(css_class="span6"),
                    css_class="row-fluid"),
                Field("about_me", rows="5"),
                ),
            )

    class Meta:
        model = UserProfile
        fields = ("first_name","last_name", "cover_profile_image", "word_one", "word_two", "word_three", "about_me")
        exclude = ["user"]

class ChefTipForm(forms.ModelForm):
    
    def __init__(self, *args, **kwargs):
        super(ChefTipForm,self).__init__(*args, **kwargs)
        self.fields["your_name"].widget = forms.TextInput(attrs={'placeholder': "To give as a reference (optional)"})
        
        
    class Meta:
        model = ChefTip
        fields=("your_name","name","tip_contact_number",)

    def clean_tip_contact_number(self):
        contact = self.cleaned_data['tip_contact_number']
        if len(contact) != 10 or not re.match('^\d+$',contact):
            raise forms.ValidationError("Please enter a valid 10 digit phone number")
        return contact    
