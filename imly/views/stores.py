from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.edit import UpdateView, CreateView
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from imly.models import Category, Store, Product, Location, Tag
from imly.forms import StoreForm, OrderItemForm

import plata
from plata.shop.models import Order, OrderItem

# how to confirm store is owned by person editing it?
"""
store_info = {
    "queryset" : Store.objects.is_approved().all(),
    "template_name" : "store_list.html"
}"""

def home_page(request):
    return render(request,"index.html")

class StoreList(ListView):
    
    model = Store
    template_name = "store_list.html"
    paginate_by = 12
    
    def get_queryset(self):
        if not self.request.session.get("place_slug",""):
            store_list = Store.objects.all()
        else:
            location = Location.objects.get(slug = self.request.session["place_slug"])
            store_list = location.store_set.all()
        self.tags = Tag.objects.filter(slug__in=self.request.GET.getlist("tags",[]))
        return store_list.filter(tags__in=self.tags).distinct() if self.tags else store_list
    
    def get_context_data(self, **kwargs):
        context = super(StoreList, self).get_context_data(**kwargs)
        context["selected_tags"] = self.tags
        return context
    

class StoresByCategory(ListView):
    
    model = Store
    template_name = "stores_by_category.html"
    paginate_by = 12
    
    def get_queryset(self):
        if not self.request.session.get("place_slug",""):
            store_list = Store.objects.all()
        else:
            location = Location.objects.get(slug=self.request.session["place_slug"])
            store_list = location.store_set.all()
        self.category = get_object_or_404(Category, slug=self.kwargs["category_slug"])
        if self.category.super_category:
            stores_by_category = store_list.filter(categories=self.category)
        else:
            stores_by_category = store_list.filter(categories__in=self.category.sub_categories.all()).distinct()
        
        self.tags = Tag.objects.filter(slug__in=self.request.GET.getlist("tags",[]))
        return stores_by_category.filter(tags__in=self.tags).distinct() if self.tags else stores_by_category
    
    def get_context_data(self, **kwargs):
        
        context = super(StoresByCategory, self).get_context_data(**kwargs)
        context["category"], context["super_category"], context["selected_tags"] = self.category, self.category.super_category or self.category, self.tags
        return context

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
        
    def get_object(self):
        return get_object_or_404(Store, owner=self.request.user)
    
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

"""
class StoreNotice(UpdateView):
    
    model=Store
    template_name="imly_store_info.html"
    form_class = StoreNotice
    
    success_url = "account/store/details"
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super(StoreNotice, self).form_valid(form)
""" 
    
class StoreInfoDetail(DetailView):
    
    model = Store
    template_name = "imly_store_info.html"
    
    def get_object(self):
        return get_object_or_404(Store, owner=self.request.user)
    
    def get(self, request, *args, **kwargs):
        try:
            self.request.user.store
            return render(request, "imly_store_info.html", {"object":request.user.store, "user":request.user})
        except Store.DoesNotExist:
            return render(request, "imly_store_info.html", {"user":request.user})

@login_required   
def store_info_detail(request):
    try:
        request.user.store
        return render(request, "imly_store_info.html", {"object":request.user.store, "user":request.user})
    except Store.DoesNotExist:
        return render(request, "imly_store_info.html", {"user":request.user})


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
    #orders = Order.objects.filter(items=OrderItem.objects.filter(product__in=user.store.product_set.all())) -- This returns only one order, of the first orderItem, actually OrderItem is needed and not Order
    model = OrderItem
    template_name = "imly_store_orders.html"
    
    def get_queryset(self):
        store = self.request.user.store#get_object_or_404(Store, slug=self.kwargs["slug"])
        return OrderItem.objects.filter(product__in=store.product_set.all())
