from django.views.generic import ListView
from django.shortcuts import get_object_or_404

from imly.models import Product, Category

class ProductsByCategory(ListView):
    
    model = Product
    template_name = "products_by_category.html"
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["category_slug"])
        return Product.objects.filter(category=self.category)