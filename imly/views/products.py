from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.db.models import Q
from imly.forms import ProductForm, OrderItemForm, UserProfileForm
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseRedirect
from imly.models import Product, Category, Store, Tag, Location, UserProfile
from reviews.forms import ReviewedItemForm
from reviews.models import ReviewedItem
from django.core.urlresolvers import reverse
from django.views.generic.edit import ModelFormMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
# how to put products by location?
#how is it finding a single product in product detail??
#how do you restrict product edit, product delete to the specific shop owner?

def coming_soon(request):
    return render(request,"coming_soon.html")

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
    template_name = "products_by_category.html"
    paginate_by = 12

    def get_queryset(self):
        products = Product.objects.is_approved().filter(is_deleted=False)
        #if self.request.session.get('place_slug', ''):
        #    products = products.filter(store__in=Location.objects.get(slug=self.request.session.get('place_slug', '')).store_set.all())
        self.category=None
        if 'category_slug' in self.kwargs:
            self.category = get_object_or_404(Category, slug=self.kwargs["category_slug"])
            products = products.filter(category=self.category) if self.category.super_category else products.filter(category__in=self.category.sub_categories.all())
        try:
            self.tags = Tag.objects.filter(slug__in=self.request.session.get("tags",[])) 
        except:
            self.tags = []
        if self.tags:
            for tag in self.tags:
                products &= tag.product_set.all()
#        raise Exception(self.request.session.get('place_slug', 'not set'))
        return products

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        if self.category:
            context["category"], context["super_category"] = self.category, self.category.super_category or self.category
        context["selected_tags"] = self.tags
        return context

# Not being used now
class ProductsByCategory(ListView):
    
    model = Product
    template_name = "products_by_category.html"
    paginate_by = 12
    
    
    def get_queryset(self):
        if not self.request.session.get("place_slug",""):
            product_list = Product.objects.all()
        else:
            location = Location.objects.get(slug=self.request.session["place_slug"])
            product_list = Product.objects.filter(store__in=location.store_set.all())
        self.category = get_object_or_404(Category, slug=self.kwargs["category_slug"])
        if self.category.super_category:
            products_by_category = product_list.filter(category=self.category)
        else:
            products_by_category = product_list.filter(category__in=self.category.sub_categories.all())
        
        products = products_by_category.is_approved()
        self.tags = Tag.objects.filter(slug__in=self.request.GET.getlist("tags",[]))
        return products.filter(tags__in=self.tags).distinct() if self.tags else products
        
            
    def get_context_data(self, **kwargs):
        context = super(ProductsByCategory, self).get_context_data(**kwargs)
        context["category"], context["super_category"], context["selected_tags"] = self.category, self.category.super_category or self.category, self.tags
        return context


class ProductCreate(CreateView):
    form_class = ProductForm
    model = Product
    template_name = "product_create.html"
    success_url = "/account/store/products/"
    
    # done to check whether product name exists since store of product is needed..
    def get_form(self, form_class):
        form = super(ProductCreate, self).get_form(form_class)
        form.instance.store = self.request.user.store
        return form

    
class ProductEdit(UpdateView):
    form_class = ProductForm
    model = Product
    template_name = "product_edit.html"
    success_url = "/account/store/products/"
    
    def get(self,request,*args, **kwargs):
        if self.get_object().store.owner != self.request.user:
            return HttpResponseForbidden()
        return super(ProductEdit,self).get(request, *args, **kwargs)

class ProductDelete(DeleteView):
    model = Product
    success_url = "/account/store/products/"
    
    def delete(self, request, *args, **kwargs):
        store = self.request.user.store
        self.object = self.get_object()
        self.object.is_deleted = True
        if store.product_set.filter(is_deleted = True).count():
            count = store.product_set.filter(is_deleted = True).count()
            self.object.position = count + 1
        else:
            count = store.product_set.filter(is_deleted = False).count()
            self.object.position = count + 100
        print self.object.position
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

@login_required
def activate_product(request,product_id):
    store = request.user.store
    product = get_object_or_404(Product,pk=product_id,store=request.user.store)
    product.is_deleted = False
    count = store.product_set.filter(is_deleted = False).count()
    product.position = count +1
    product.save()
    return HttpResponseRedirect("/account/store/products/")

class ProductsByAccount(ListView):
    
    model = Product
    template_name = "manage_products.html"   #was product_list.html
    
    
    def get_queryset(self):
        return self.request.user.store.product_set.all()
    
    def get_context_data(self, **kwargs):
        context = super(ProductsByAccount,self).get_context_data(**kwargs)
        context["active_items"] = self.request.user.store.product_set.filter(is_deleted=False)
        context["inactive_items"] = self.request.user.store.product_set.filter(is_deleted=True)
        return context
    
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

    def get_object(self, queryset=None):
        object = super(ProductDetail, self).get_object(queryset)
        return  (
                (not object.is_deleted and object.is_approved)
                or (self.request.user.is_authenticated() and self.request.user == object.store.owner)
                )  and object

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        return  object and super(ProductDetail, self).get(request, *args, **kwargs) or redirect(reverse('imly_coming_soon'))

@csrf_exempt
@login_required
def sort_product(request):
    for index, product_id in enumerate(request.POST.getlist('product[]')):
        product = get_object_or_404(Product,id=int(str(product_id)), store=request.user.store)
        product.position = index
        product.save()
        print product.position
    return HttpResponse('Success')