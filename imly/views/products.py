from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import get_object_or_404, render, render_to_response, redirect
from django.db.models import Q
from imly.forms import ProductForm, OrderItemForm, UserProfileForm
from django.http import HttpResponseForbidden,HttpResponse, HttpResponseRedirect
from imly.models import Product, Category, Store, Tag, Location, UserProfile, Special, City, Wish
from reviews.forms import ReviewedItemForm
from reviews.models import ReviewedItem
from django.core.urlresolvers import reverse
from django.views.generic.edit import ModelFormMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point, MultiPolygon
from django.contrib.gis.measure import D
from imly.utils import tracker
from django.contrib.auth.models import User
from django.template import RequestContext
import json as simplejson
# how to put products by location?
#how is it finding a single product in product detail??
#how do you restrict product edit, product delete to the specific shop owner?

def coming_soon(request):
    return render(request,"coming_soon.html")

class SpecialList(ListView):
    model = Product
    template_name = 'special_products.html'

    def get_queryset(self):
        special = get_object_or_404(Special, slug=self.kwargs['slug'], active=True)
        self.request.special = special
        products = special.products.is_approved()
        if self.request.city:
            products = products.filter(store__delivery_locations__location__within=self.request.city.enclosing_geometry) | products.filter(store__pick_up_point__within=self.request.city.enclosing_geometry)
        return products.distinct()

class ProductReview(CreateView):
    form_class = ReviewedItemForm
    model = ReviewedItem
    template_name = "imly_product_detail.html"

    def get_success_url(self):
        reviewed_item = self.object
        tracker.add_event('review-created', {'product': self.object.content_object.slug, 'store': self.object.content_object.store.slug})
        return reverse("imly_product_detail", args = (reviewed_item.content_object.store.slug,reviewed_item.content_object.slug,))

    def form_valid(self,form):
        reviewed_item = form.save(commit=False)
        reviewed_item.user = self.request.user
        reviewed_item.content_object = Product.objects.get(slug=self.request.POST.get("product_slug"), store__slug=self.request.POST.get('store_slug'))
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
    #paginate_by = 12

    def get_queryset(self):
        products = Product.objects.is_approved().filter(is_deleted=False,is_flag=False)
        if self.request.session.get("place_slug",""):
            user_point = self.request.session.get("bingeo")
            user_point = Point(*user_point)
            products = products.distance(user_point).order_by("distance")
        if self.request.session.get('delivery', None) and self.request.city.name=="Mumbai":
            if self.request.session.get('place_slug', None):
                try:
                    pilot_city = City.objects.get(slug="fbn-pilot")
                    if user_point.within(pilot_city.enclosing_geometry):
                        products = products.filter(Q(store__pick_up_point__within=pilot_city.enclosing_geometry)| (Q(store__delivery_locations__location__within=self.request.city.enclosing_geometry) & Q(store__delivery_locations__location__distance_lte=(user_point, D(km=3)))))
                    else:
                        products = products.filter(store__delivery_locations__location__within=self.request.city.enclosing_geometry).filter(store__delivery_locations__location__distance_lte=(user_point, D(km=3)))
                except City.DoesNotExist:
                    pass # no pilot city found
#            else:
#                products = products.filter(store__delivery_locations__location__within=self.request.city.enclosing_geometry)
        else:
             products = products.filter(store__pick_up_point__within=self.request.city.enclosing_geometry)
        self.category=None
        if 'category_slug' in self.kwargs:
            self.category = get_object_or_404(Category, slug=self.kwargs["category_slug"])
            products = products.filter(category=self.category).distinct() if self.category.super_category else products.filter(category__in=self.category.sub_categories.all()).distinct()
        try:
            self.tags = Tag.objects.filter(slug__in=self.request.session.get("tags",[]))
        except:
            self.tags = []
        if self.tags:
            products = products.distinct()
            for tag in self.tags:
                products &= tag.product_set.distinct()
        return products.distinct()

    def get_context_data(self, **kwargs):
        context = super(ProductList, self).get_context_data(**kwargs)
        if self.category:
            context["category"], context["super_category"] = self.category, self.category.super_category or self.category
        context["selected_tags"] = self.tags
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
        context["active_items"] = self.request.user.store.product_set.filter(is_deleted=False,is_flag=False)
        context["inactive_items"] = self.request.user.store.product_set.filter(is_deleted=True)
        context["flag"] = self.request.user.store.product_set.filter(is_flag=True)
        try:
            context["special_event"] = Special.objects.filter(active = True, chef_can_tag=True).order_by('priority')[0]
        except IndexError:
            pass
        return context

class ProductDetail(DetailView):

    model = Product
    template_name = "imly_product_detail.html"

    def get_context_data(self, **kwargs):
        context = super(ProductDetail, self).get_context_data(**kwargs)
        context["form"] = OrderItemForm()
        context["review_form"] = ReviewedItemForm()
        context["other_store_products"] = self.get_object().store.product_set.filter(is_flag=False).exclude(is_deleted = True)
        context["product_count"] = self.get_object().store.product_set.filter(is_flag=False).count()
        if self.request.session.get("place_slug",""):
            user_point = self.request.session.get("bingeo")

            user_point = Point(*user_point)
            print user_point
            store_point = self.get_object().store.pick_up_point
        return context

    def get_queryset(self):
        store = get_object_or_404(Store, slug=self.kwargs["store_slug"])
        return store.product_set.all()

    def get_object(self, queryset=None):
        object = super(ProductDetail, self).get_object(queryset)
        return  ((not object.is_deleted and object.is_approved)
                or (self.request.user.is_authenticated() and (self.request.user.is_staff or self.request.user == object.store.owner) )) and object

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

@login_required
def special_event(request,event_slug,product_slug):
    event = Special.objects.get(slug=event_slug)
    product = Product.objects.get(slug=product_slug,store=request.user.store)
    event.products.add(product)
    event.save()
    return redirect('imly_store_products')

@login_required
def unsubscribe_event(request,event_slug,product_slug):
    event = Special.objects.get(slug=event_slug)
    product = Product.objects.get(slug=product_slug,store=request.user.store)
    event.products.remove(product)
    event.save()
    return redirect('imly_store_products')

@csrf_exempt
def wish_product(request):
    product = Product.objects.get(slug = request.POST.get('product_slug'),store=Store.objects.get(slug = request.POST.get('store_slug')))
    Wish.objects.create(user=User.objects.get(pk=request.POST.get('user_id')),product=product)
    return HttpResponse("success");

@csrf_exempt
@login_required
def remove_product(request):
    product = Product.objects.get(slug = request.POST.get('product_slug'),store=Store.objects.get(slug = request.POST.get('store_slug')))
    user = User.objects.get(pk=request.POST.get('user_id'))
    store = product.store
    wish = Wish.objects.get(user=user,product=product,is_active=True)
    wish.is_active = False
    wish.save()
    data = {'count':user.wish_set.exclude(is_active = False).count(), "store_wish_count":store.product_set.filter(wish__in=Wish.objects.filter(user=user, is_active=True)).count()}
    return HttpResponse(simplejson.dumps(data),mimetype="application/json")

@login_required
def wishlist(request):
    wish_products = Wish.objects.filter(user=request.user,is_active = True)
    store_set=set()
    for wish in wish_products:
        store_set.add(wish.product.store)
    return render_to_response('wish_products.html',locals(),RequestContext(request))
    
