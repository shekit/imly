from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from imly.models import Category, Store


class StoresByCategory(ListView):
    
    model = Store
    template_name = "stores_by_category.html"
    
    def get_queryset(self):
        self.categories = get_object_or_404(Category, slug=self.kwargs["category_slug"])
        return Store.objects.filter(categories=self.categories)