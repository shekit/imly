from django import forms
from imly.models import Store

class StoreForm(forms.ModelForm):
    
    class Meta:
        model = Store
        exclude = ["slug","date_created","date_updated", "is_featured","is_approved"]