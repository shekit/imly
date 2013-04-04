from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, render, render_to_response
from django.template import RequestContext, Context
from imly.forms import ProductForm, OrderItemForm, UserProfileForm
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from imly.models import Product, Category, Store, Tag, Location, UserProfile

# how to put products by location?
#how is it finding a single product in product detail??
#how do you restrict product edit, product delete to the specific shop owner?

def coming_soon(request):
    return render(request,"coming_soon.html")

'''def my_profile(request,template="imly_my_profile.html"):
    owner=request.user
    return render_to_response(template, locals(), RequestContext(request))'''

class ProfileInfo(DetailView):
    model = UserProfile
    template_name = "imly_my_profile.html"

    def get_object(self):
        return get_object_or_404(UserProfile,user=self.request.user)

    def get(self,request,*args,**kwargs):
        try:
            self.request.user.userprofile
            return render(request,"imly_my_profile.html",{"object":request.user.userprofile,"user":request.user})
        except UserProfile.DoesNotExist:
            return render(request,"imly_my_profile.html",{"user":request.user})

'''def create_profile(request,template="imly_create_profile.html"):
    #user = User.objects.get(username=request.user)
    #profile_ins = UserProfile.objects.get(user=user)
    if request.method == 'POST':
        profile = UserProfileForm(request.POST,request.FILES)
        if profile.is_valid():
            newprofile=profile.save(commit=False)
            newprofile.user = request.user
            newprofile.save()
            return HttpResponseRedirect('/account/store/my_profile/')
    else:
        profile = UserProfileForm()
    return render_to_response(template,locals(),RequestContext(request))'''

class ProfileCreate(CreateView):
    form_class = UserProfileForm
    model = UserProfile
    template_name = "imly_create_profile.html"
    success_url = "/account/store/my_profile/"
    
    def form_valid(self,form):
        form.instance.user = self.request.user
        return super(ProfileCreate,self).form_valid(form)

'''def edit_profile(request,template="imly_edit_profile.html"):
    user = User.objects.get(username=request.user)
    profile_ins = UserProfile.objects.get(user=user)
    if request.method == 'POST':
        profile = UserProfileForm(request.POST,request.FILES,instance=profile_ins)
        if profile.is_valid():
            newprofile = profile.save(commit=False)
            newprofile.user = request.user
            newprofile.save()
            return HttpResponseRedirect('/account/store/my_profile')
    else:
        profile = UserProfileForm(instance=profile_ins)
    return render_to_response(template,locals(),RequestContext(request))'''

class EditProfile(UpdateView):
    form_class = UserProfileForm
    model = UserProfile
    template_name = "imly_edit_profile.html"
    success_url = "/account/store/my_profile/"
    
    def get(self,request,*args, **kwargs):
        if self.get_object().user != self.request.user:
            return HttpResponseForbidden()
        return super(EditProfile,self).get(request, *args, **kwargs)



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
    
    def form_valid(self,form):
        form.instance.store = self.request.user.store
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
    