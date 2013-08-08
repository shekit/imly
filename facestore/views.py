from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.views.generic import DetailView
from fb.modules.profile.page.models import Page
from django.shortcuts import get_object_or_404, redirect, render,render_to_response
from imly.models import Store, Special, Product
from imly.forms import OrderItemForm
import plata
from plata.shop.models import OrderItem, Order
from plata.shop.forms import ConfirmationForm
from django.forms.models import inlineformset_factory
from plata.contact.forms import CheckoutForm
import json as simplejson


def home(request):
    if request.fb_session.signed_request:
        # request is from facebook
        page_info=request.fb_session.signed_request['page']
        if "tabs_added" in request.META["QUERY_STRING"]:
            store = request.user.store
            store.page=page_info["id"]
            store.save()
            return redirect("http://facebook.com/pages/imly/"+page_info['id']+'?id='+page_info['id']+'&sk=app_'+str(settings.FACEBOOK_APPS['facestore']['ID']))
        else:
            store = Store.objects.get(page=page_info["id"])
            products = store.product_set.filter(is_flag=False, is_deleted = False)
            try:
                special_event = Special.objects.filter(active=True, live=True).order_by("priority")[0]
                special_products = special_event.products.filter(store=store)
                products = products.exclude(special=special_event)
            except IndexError:
                pass
            return render(request, "facebook_store/fb_product_list.html", locals())
    else:
        return HttpResponse('oye, some wanderer on net, get lost you troll')

class FBProductDetail(DetailView):
    model = Product
    template_name = "facebook_store/fb_product_detail.html"
    
    def get_context_data(self, **kwargs):
        context = super(FBProductDetail,self).get_context_data(**kwargs)
        context["form"] = OrderItemForm()
        try:
            special_event = Special.objects.filter(active=True, live=True).order_by("priority")[0]
            if special_event:
                context["special_event"] = special_event
                context["special_product"] = self.get_object().special_set.filter(slug=special_event.slug)
        except IndexError:
            pass
        context["store"] = self.get_object().store
        return context
        
    def get_queryset(self):
        store = get_object_or_404(Store,slug=self.kwargs["store_slug"])
        return store.product_set.all()
    
    def get_object(self, queryset=None):
        object = super(FBProductDetail, self).get_object(queryset)
        return  (not object.is_deleted and object.is_approved) and object
    
def fb_add_order(request, store_slug, product_slug):
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

    return render(request, "fb_product_detail.html", {"object":product, "form":form})

def fb_one_step_checkout(request):
    shop = plata.shop_instance()
    order = shop.order_from_request(request)
    if order:
        order.data["from_facebook"] = True   #to check whether refering page is from facebook or imly
    #store = order.storeorder_set.get(order=order).store
    page_info=request.fb_session.signed_request['page']
    #page = Page.objects.get(pk=page_info['id'])
    store = Store.objects.get(page=page_info["id"])
    OrderItemFormset = inlineformset_factory(Order,OrderItem,extra=0,fields=('quantity',),)
    orderitemformset=OrderItemFormset(instance=order)
    try:
        order.validate(order.VALIDATE_CART)
    except AttributeError:
        return render(request, "facebook_store/fb_empty_cart.html")
    except ValidationError, e:
        for message in e.messages:
            messages.error(request, message)
        return redirect(reverse('fb_checkout'))
    if '_checkout' in request.POST:
        orderform = CheckoutForm(request.POST, **{"prefix":"order", "instance":order,"request":request,"shop":shop})
        form = ConfirmationForm(request.POST, **{"order":order,"request":request, "shop":shop})
    else:
        orderform = CheckoutForm(**{"prefix":"order", "instance":order,"request":request,"shop":shop})
        form = ConfirmationForm(initial={"terms_and_conditions":True,"payment_method":"plata.payment.modules.cod"},**{"order":order,"request":request, "shop":shop})
    if form.is_valid() and orderform.is_valid():
        shop.checkout(request, order)
        return shop.confirmation(request,order)
    return render(request, "facebook_store/fb_one_step_checkout.html", locals())
