from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.edit import UpdateView, CreateView
from django.http import HttpResponseForbidden

from imly.models import Category, Store, Product, Location
from imly.forms import StoreForm, OrderItemForm

import plata

# how to confirm store is owned by person editing it?

class StoresByCategory(ListView):
    
    model = Store
    template_name = "stores_by_category.html"
    
    def get_queryset(self):
        categories = get_object_or_404(Category, slug=self.kwargs["category_slug"])
        return Store.objects.filter(categories=categories)

class StoresByPlace(ListView):
    
    model = Store
    template_name = "stores_by_place.html"
    
    def get_queryset(self):
        place = get_object_or_404(Location, slug=self.kwargs["place_slug"])
        return Store.objects.filter(delivery_areas=place)

class StoreEdit(UpdateView):
    
    form_class= StoreForm
    model = Store
    template_name="store_edit.html"
    
    success_url = "/account/store/products/"

    #forbidding everything..why??      
    def get(self,request, *args, **kwargs):
        if self.get_object().owner == self.request.user:
            return super(StoreEdit, self).get(request,*args, **kwargs)
        else:
            return HttpResponseForbidden()
    
class StoreCreate(CreateView):
    
    form_class = StoreForm
    model = Store
    template_name = "store_create.html"
    
    success_url = "/account/store/products"
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(StoreCreate, self).form_valid(form)    
    
    
    def get(self, request, *args, **kwargs):
        try:
            self.request.user.store
            return redirect("imly_store_products")
        except Store.DoesNotExist:
            return super(StoreCreate, self).get(request, *args, **kwargs)
        

class StoreDetail(DetailView):
    
    model = Store
    template_name = "imly_store_detail.html"
    
class StoreInfoDetail(DetailView):
    
    model = Store
    template_name = "imly_store_info.html"


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

class OrderList(ListView):
    pass
    #orders = Order.objects.filter(items=OrderItem.objects.filter(product__in=user.store.product_set()))
