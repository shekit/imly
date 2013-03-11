from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404
from imly.forms import ProductForm, OrderItemForm
from django.http import HttpResponseForbidden

from imly.models import Product, Category, Store

# how to put products by location?
#how is it finding a single product in product detail??
#how do you restrict product edit, product delete to the specific shop owner?

class ProductsByCategory(ListView):
    
    model = Product
    template_name = "products_by_category.html"
    
    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs["category_slug"])
        return Product.objects.filter(category=category)
    
class ProductsByPlace(ListView):
    
    model = Product
    template_name = "products_by_place.html"
    
    def get_queryset(self):
        place = get_object_or_404(Location, slug=self.kwargs["place_slug"])
        return self.model.objects.filter(store__in=Store.objects.filter(delivery_areas=place))

class ProductCreate(CreateView):
    form_class = ProductForm
    model = Product
    success_url = "/account/store/products/"
    
    def form_valid(self,form):
        form.instance.store = self.request.user.store
        return super(ProductCreate,self).form_valid(form)
    
    
class ProductEdit(UpdateView):
    form_class = ProductForm
    model = Product
    success_url = "/account/store/products/"
    
    def get(self,request,*args, **kwargs):
        if self.get_object().store.owner != self.request.user:
            return HttpResponseForbidden()
        return super(ProductEdit,self).get(request, *args, **kwargs)
    
class ProductDelete(DeleteView):
    model = Product
    success_url = "/account/store/products/"
    
    def get(self,request, *args,**kwargs):
        if self.get_object().store.owner != self.request.user:
            return HttpResponseForbidden()
        return super(ProductDelete, self).get(request, *args, **kwargs)
    
class ProductsByAccount(ListView):
    
    model = Product
    template_name = "manage_products.html"   #was product_list.html
    
    
    def get_queryset(self):
        return self.request.user.store.product_set.all()
    

    
class ProductDetail(DetailView):
    
    model = Product
    template_name = "imly_product_detail.html"
    
    def get_context_data(self, **kwargs):
        
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context["form"] = OrderItemForm()
        return context
    
    def get_queryset(self):
        store = get_object_or_404(Store, slug=self.kwargs["store_slug"])
        return store.product_set.all()
    