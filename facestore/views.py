from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.views.generic import DetailView
from facebook.modules.profile.page.models import Page
from django.shortcuts import get_object_or_404, redirect, render,render_to_response
from imly.models import Store, Special, Product
from imly.forms import OrderItemForm
import plata
from plata.shop.models import OrderItem, Order
import json as simplejson


def home(request):
    if request.fb_session.signed_request:
        # request is from facebook
        page_info=request.fb_session.signed_request['page']
        if request.GET.get('tabs_added['+page_info['id']+']', None):
            page = Page(id=page_info['id'])
            page.get_from_facebook(save=True)
            store = request.user.store
            store.page=page
            store.save()
            return HttpResponse('imly store just added')
        else:
            page = Page.objects.get(pk=page_info['id'])
            store = Store.objects.get(page=page)
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
    