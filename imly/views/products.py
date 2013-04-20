from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.template import RequestContext, Context
from imly.forms import ProductForm, OrderItemForm, UserProfileForm
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from imly.models import Product, Category, Store, Tag, Location, UserProfile
from reviews.forms import ReviewedItemForm
from reviews.models import ReviewedItem
from django.core.urlresolvers import reverse
from django.views.generic.edit import ModelFormMixin
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
# how to put products by location?
#how is it finding a single product in product detail??
#how do you restrict product edit, product delete to the specific shop owner?

def coming_soon(request):
    return render(request,"coming_soon.html")

#def set_review(request):
#    return redirect(request.POST.get("next"))


class ProductReview(CreateView):
    form_class = ReviewedItemForm
    model = ReviewedItem
    template_name = "imly_product_detail.html"
    
    def get_success_url(self):
        reviewed_item = self.object
        return reverse("imly_product_detail", args = (reviewed_item.content_object.store.slug,reviewed_item.content_object.slug,))
    
    def form_valid(self,form):
        reviewed_item = form.save(commit=False)
        reviewed_item.user = self.request.user
        reviewed_item.content_object = Product.objects.get(slug=self.request.POST.get("product_slug"))
        self.object = form.save()
        return super(ModelFormMixin,self).form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(ProductReview, self).get_context_data(**kwargs)
        context["review_form"] = self.get_form(self.get_form_class())
        context["object"] = Product.objects.get(slug=self.request.POST.get("product_slug"))
        context["form"] = OrderItemForm()
        return context

        
class ProductList(ListView):
    
    model = Product
    template_name = "product_list.html"
    paginate_by = 12
    
    def get_queryset(self):
        if not self.request.session.get("place_slug",""):
            product_list = Product.objects.is_approved().all()
            
        else:
            location = Location.objects.get(slug = self.request.session["place_slug"])
            product_list = Product.objects.filter(store__in=location.store_set.is_approved().all())
        self.tags = Tag.objects.filter(slug__in=self.request.GET.getlist("tags",[]))
        return product_list.filter(tags__in=self.tags).distinct() if self.tags else product_list
    
    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        context["selected_tags"] = self.tags
        return context

class ProductsByCategory(ListView):
    
    model = Product
    template_name = "products_by_category.html"
    paginate_by = 12
    
    
    def get_queryset(self):
        if not self.request.session.get("place_slug",""):
            product_list = Product.objects.is_approved().all()
        else:
            location = Location.objects.get(slug=self.request.session["place_slug"])
            product_list = Product.objects.filter(store__in=location.store_set.is_approved().all())
        self.category = get_object_or_404(Category, slug=self.kwargs["category_slug"])
        if self.category.super_category:
            products_by_category = product_list.filter(category=self.category)
        else:
            products_by_category = product_list.filter(category__in=self.category.sub_categories.all())
        
        
        self.tags = Tag.objects.filter(slug__in=self.request.GET.getlist("tags",[]))
        return products_by_category.filter(tags__in=self.tags).distinct() if self.tags else products_by_category
        
            
    def get_context_data(self, **kwargs):
        
        #raise exceptions.Exception(self.request.GET.getlist("tags",[]))
        context = super(ProductsByCategory, self).get_context_data(**kwargs)
        context["category"], context["super_category"], context["selected_tags"] = self.category, self.category.super_category or self.category, self.tags
        return context
    
class ProductsByPlace(ListView):
    
    model = Product
    template_name = "products_by_place.html"
    
    def get_queryset(self):
        place = get_object_or_404(Location, slug=self.kwargs["place_slug"])
        return self.model.objects.is_approved().filter(store__in=Store.objects.filter(delivery_areas=place))

class ProductCreate(CreateView):
    form_class = ProductForm
    model = Product
    template_name = "product_create.html"
    success_url = "/account/store/products/"

    def get_form(self, form_class):
        form = super(ProductCreate, self).get_form(form_class)
        form.instance.store = self.request.user.store
        return form

    def form_valid(self,form):
        return super(ProductCreate,self).form_valid(form)

    
class ProductEdit(UpdateView):
    form_class = ProductForm
    model = Product
    template_name = "product_edit.html"
    success_url = "/account/store/products/"
    
    def get(self,request,*args, **kwargs):
        if self.get_object().store.owner != self.request.user:
            return HttpResponseForbidden()
        return super(ProductEdit,self).get(request, *args, **kwargs)
    
def delete_product(request,product_id):
    product = Product.objects.get(pk=product_id)
    product.is_deleted = True
    product.save()
    return HttpResponseRedirect("/account/store/products/")

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
        context["review_form"] = ReviewedItemForm()
        return context
    
    def get_queryset(self):
        store = get_object_or_404(Store, slug=self.kwargs["store_slug"])
        return store.product_set.all()
    