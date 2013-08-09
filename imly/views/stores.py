from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404, redirect, render,render_to_response
from django.views.generic.edit import UpdateView, CreateView
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseForbidden,HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q, F
from imly.models import Category, Store, Product, Location, Tag, StoreOrder, Special, City
from imly.forms import StoreForm, OrderItemForm,DeliveryLocationFormSet
from django.contrib.gis.geos import Point, MultiPolygon
from django.contrib.gis.measure import D
import plata
from plata.shop.forms import ConfirmationForm
from plata.shop.models import OrderItem, Order
from plata.contact.forms import CheckoutForm
from imly.utils import tracker
import json as simplejson
from datetime import date



def home_page(request):
    city_stores = Store.objects.is_approved().filter(Q(pick_up_point__within=request.city.enclosing_geometry) | Q(delivery_locations__location__within=request.city.enclosing_geometry))
    city_products = Product.objects.is_approved().filter(store__in=city_stores)
    bestselling_products = city_products.filter(is_bestseller=True, is_deleted=False,is_flag = False)[:4]
    featured_stores = city_stores.filter(is_featured=True)[:4]
    recently_added = city_products.filter(is_deleted=False, is_flag=False).order_by("-date_created")[:8]
    recently_bought = city_products.filter(orderitem__order__status__gte=0).order_by("-orderitem__order__created")[:8]
    try:
        special_event = Special.objects.filter(active=True, live=True).order_by("priority")[0]
        special_products = special_event.products.all()[:4]
    except IndexError:
        pass
    return render(request,"index.html", locals())

def why_open_your_shop(request):
    return render(request, "open_your_shop.html")

def contact_us(request):
    return render(request,"contact.html")

def faqs(request):
    return render(request, "faqs.html")

def what_is_imly(request):
    return render(request, "what_is_imly.html")

def wrong_location(request):
    return render(request, "no_location.html")

def no_city(request):
    return render(request, "no_city_yet.html")

def not_in_city(request):
    return render(request, "not_in_city.html")

class StoreList(ListView):

    model = Store
    template_name = "stores_by_category.html"

    def get_queryset(self):
        stores = Store.objects.filter(is_approved=True)
        if self.request.session.get("place_slug",""):
            user_point = self.request.session.get('bingeo')
            user_point = Point(*user_point)
            stores = stores.distance(user_point).order_by('distance')
        stores = stores.filter(pick_up_point__within=self.request.city.enclosing_geometry)
        self.category=None
        if "category_slug" in self.kwargs:
            self.category = get_object_or_404(Category, slug=self.kwargs["category_slug"])
            stores = stores.filter(categories=self.category) if self.category.super_category else stores.filter(categories__in=self.category.sub_categories.all()).distinct()
        stores = stores.distinct()
        try:
            self.tags = Tag.objects.filter(slug__in=self.request.session.get("tags",[]))
        except:
            self.tags = []
        if self.tags:
            for tag in self.tags:
                stores &= tag.store_set.distinct()
        return stores

    def get_context_data(self, **kwargs):
        context = super(StoreList, self).get_context_data(**kwargs)

        if self.category:
            context["category"], context["super_category"] = self.category, self.category.super_category or self.category
        context["selected_tags"] = self.tags
        return context

class StoreEdit(UpdateView):

    form_class= StoreForm
    model = Store
    template_name="store_edit.html"

    success_url = "/account/store/details/"

    #forbidding everything..why??
    def get(self,request, *args, **kwargs):
        if self.get_object().owner == self.request.user:
            return super(StoreEdit, self).get(request,*args, **kwargs)
        else:
            return HttpResponseForbidden()

    def post(self, request, *args, **kwargs):
        super_return = super(StoreEdit, self).post(request, *args, **kwargs)
        delivery_formset = DeliveryLocationFormSet(self.request.POST, instance=self.get_object())
        if delivery_formset.is_valid():
            delivery_formset.save()
            return super_return
        else:
            return self.form_invalid()

    def get_object(self):
        return get_object_or_404(Store, owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(StoreEdit, self).get_context_data(**kwargs)
        store = self.get_object()
        if self.request.POST:
            context['delivery_location_form'] = DeliveryLocationFormSet(self.request.POST, queryset=store.delivery_locations.all(),instance=store)
        else:
            context['delivery_location_form'] = DeliveryLocationFormSet(queryset=store.delivery_locations.all(),instance=store)
        return context

class StoreCreate(CreateView):
    form_class = StoreForm
    model = Store
    template_name = "store_create.html"
    success_url = "/account/store/products"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        context = self.get_context_data()
        delivery_location_form = context['delivery_location_form']
        store = form.save()
        delivery_location_form.instance = store
        if delivery_location_form.is_valid():
            delivery_location_form.save()
            tracker.add_event('store-create', {'store': store.slug})
            return HttpResponseRedirect(self.success_url)
        else:
            return self.form_invalid(form)
        return super(StoreCreate, self).form_valid(form)

    def get(self, request, *args, **kwargs):
        try:
            self.request.user.store
            return redirect("imly_store_products")
        except Store.DoesNotExist:
            return super(StoreCreate, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(StoreCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            context['delivery_location_form'] = DeliveryLocationFormSet(self.request.POST)
        else:
            context['delivery_location_form'] = DeliveryLocationFormSet()
        return context


class StoreDetail(DetailView):
    ''' Public View/Store Preview detail view'''
    model = Store
    template_name = "imly_store_detail.html"

    def get_object(self, queryset=None):
        object = super(StoreDetail, self).get_object(queryset)
        return (object.is_approved or
                (self.request.user.is_authenticated()
                 and (object.owner == self.request.user or self.request.user.is_staff))) and object

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        return object and super(StoreDetail, self).get(request, *args, **kwargs) or redirect(reverse('imly_coming_soon'))

    def get_context_data(self, **kwargs):
        context = super(StoreDetail, self).get_context_data(**kwargs)
        context['products'] = self.get_object().product_set.filter(is_flag=False).exclude(is_deleted=True)
        context['product_count'] = self.get_object().product_set.filter(is_deleted=False,is_flag=False).count()
        return context

class StoreInfoDetail(DetailView):
    ''' Account view of store information '''
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
def status(request):
    store = request.user.store
    if store.is_open == False:
        store.is_open = True
    else:
        store.is_open = False
    store.save()
    return HttpResponseRedirect("/account/store/details/")

@login_required
def store_info_detail(request):
    try:
        request.user.store
        return render(request, "imly_store_info.html", {"object":request.user.store, "user":request.user})
    except Store.DoesNotExist:
        return render(request, "imly_store_info.html", {"user":request.user})


def add_order(request, store_slug, product_slug):
    shop = plata.shop_instance()

    product = get_object_or_404(Product, slug=product_slug, store__slug=store_slug)


    if request.method == "POST":
        form = OrderItemForm(data=request.POST)

        if form.is_valid():
            order = shop.order_from_request(request,create=True)
            stock_change = product.stock_change(order)
            quantity = form.cleaned_data["quantity"]
            if quantity > stock_change:
                data = {"success":False,"product_slug":product.slug}
                '''messages.error(request, "I can only make %d more %ss today" %(product.items_in_stock, product.name))
                return render(request, "imly_product_detail.html", {"object":product, "form":form})'''
                return HttpResponse(simplejson.dumps(data),mimetype="application/json")
            order.modify_item(product, relative=form.cleaned_data["quantity"])

            try:
                messages.success(request,"The cart has been updated")
            except ValidationError, e:
                if e.code == "order_sealed":
                    pass
                else:
                    raise
            #return redirect("plata_shop_cart")
            data = {"success":True,"count":order.items.count(),"product":product.name.lower(),"product_slug":product.slug, "items_in_stock":product.items_in_stock - quantity,"store":product.store.name.lower(),"quantity":quantity,"image":product.image_thumbnail_mini.url}
            return HttpResponse(simplejson.dumps(data),mimetype="application/json")
    else:
        form = OrderItemForm()

    return render(request, "imly_product_detail.html", {"object":product, "form":form})

def one_step_checkout(request):
    shop = plata.shop_instance()
    order = shop.order_from_request(request)
    if not order or not order.items.count():# or order.created.date() < date.today(): #added last part to check for stale orders in cart
        return redirect(reverse('plata_shop_cart'))
    try:
        order.validate(order.VALIDATE_CART)
    except ValidationError, e:
        for message in e.messages:
            messages.error(request, message)
        return HttpResponseRedirect(reverse('plata_shop_cart'))
    if '_checkout' in request.POST:
        orderform = CheckoutForm(request.POST, **{"prefix":"order", "instance":order,"request":request,"shop":shop})
        form = ConfirmationForm(request.POST, **{"order":order,"request":request, "shop":shop})
    else:
        orderform = CheckoutForm(**{"prefix":"order", "instance":order,"request":request,"shop":shop})
        form = ConfirmationForm(initial={"terms_and_conditions":True,"payment_method":"plata.payment.modules.cod"},**{"order":order,"request":request, "shop":shop})
    if form.is_valid() and orderform.is_valid():
        shop.checkout(request, order)
        return shop.confirmation(request,order)
    return render(request, "one_step_checkout.html", locals())
        
class OrderList(ListView):
    #orders = Order.objects.filter(items=OrderItem.objects.filter(product__in=user.store.product_set.all())) -- This returns only one order, of the first orderItem, actually OrderItem is needed and not Order
    model = OrderItem
    template_name = "imly_store_orders.html"

    def get_queryset(self):
        store = self.request.user.store#get_object_or_404(Store, slug=self.kwargs["slug"])
        return OrderItem.objects.filter(product__in=store.product_set.all())

@csrf_exempt
def  update_store_order(request):
    store_order = StoreOrder.objects.get(pk=request.POST.get('store_order_id'))
    update_parameter = [key for key in request.POST.keys() if key != 'store_order_id'][0]
    value = request.POST.get(update_parameter)
    if update_parameter != 'note':
        value = int(value)
    store_order.__setattr__(update_parameter, value)
    store_order.save()
    return HttpResponse('Succesfully Updated')