from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.edit import UpdateView

from imly.models import Category, Store, Product
from imly.forms import StoreForm, OrderItemForm

import plata

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
    

def add_order(request, product_slug):
    shop = plata.shop_instance()
    
    product = get_object_or_404(Product, slug=product_slug)
    
    if request.method == "POST":
        form = OrderItemForm(data=request.POST)
        
        if form.is_valid():
            order = shop.order_from_request(request,create=True)
            order.modify_item(product, relative=form.cleaned_data["quantity"])
            """try:
                
                #messages.success(request, _("The cart has been updated"))
            except form.ValidationError, e:
                if e.code == "order_sealed":
                    pass
                else:
                    raise"""
            return redirect("plata_shop_cart")
        
    else:
        form = OrderItemForm()
        
    return render(request, "imly_product_detail.html", {"object":product, "form":form})
