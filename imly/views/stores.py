from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.views.generic.edit import UpdateView

from imly.models import Category, Store
from imly.forms import StoreForm

class StoresByCategory(ListView):
    
    model = Store
    template_name = "stores_by_category.html"
    
    def get_queryset(self):
        self.categories = get_object_or_404(Category, slug=self.kwargs["category_slug"])
        return Store.objects.filter(categories=self.categories)
    

class StoreEdit(UpdateView):
    
    form_class= StoreForm
    model = Store
    template_name="store_edit.html"
    
    success_url = "/account/store/products/"
    
    def get_queryset(self):
        return Store.objects.all()
    
    
