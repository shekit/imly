from django.conf.urls import patterns, include, url
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from imly.models import Product, Store, Category, Location


from imly.views.stores import StoreCreate, StoreDetail, StoreEdit, StoresByCategory, StoresByPlace, StoreInfoDetail, OrderList
from imly.views.products import ProductsByCategory, ProductCreate, ProductDelete, ProductDetail, ProductEdit, ProductsByAccount

from plata.contact.models import Contact
from plata.discount.models import Discount
from plata.shop.models import Order
from plata.shop.views import Shop

shop = Shop(
    contact_model=Contact,
    order_model=Order,
    discount_model=Discount,
    default_currency= "INR",
    )

product_info = {
    "queryset" : Product.objects.all(),
    "template_name" : "product_list.html"
}

store_info = {
    "queryset" : Store.objects.all(),
    "template_name" : "store_list.html"
}

category_info = {
    "queryset" : Category.objects.all(),
    "template_name":"category_list.html"
}

location_info = {
    "queryset" : Location.objects.all(),
    "template_name":"location_list.html"
}

urlpatterns = patterns('',
    
    url(r"^stores/$", ListView.as_view(**store_info), name="imly_store_list"),
    url(r"^stores/(?P<slug>[-\w]+)/$", StoreDetail.as_view() , name="imly_store_detail"),
    url(r"^account/store/create/$", login_required(StoreCreate.as_view()), name ="imly_store_create"),
    url(r"^account/store/(?P<slug>[-\w]+)/details", login_required(StoreInfoDetail.as_view()), name ="imly_store_info"),
    url(r"^account/store/(?P<slug>[-\w]+)/edit/$", login_required(StoreEdit.as_view()), name="imly_store_edit"),
    url(r"^account/store/(?P<slug>[-\w]+)/orders/$", login_required(OrderList.as_view()), name="imly_store_orders"),
    
)

urlpatterns += patterns('',
    
    url(r"^products/$", ListView.as_view(**product_info), name="imly_product_list"),
    url(r"^stores/(?P<store_slug>[-\w]+)/products/(?P<slug>[-\w]+)/$", ProductDetail.as_view(), name="imly_product_detail"),
    
)

urlpatterns += patterns('',
    
    url(r"^categories/$", ListView.as_view(**category_info), name="imly_category_list" ),
    url(r"^categories/(?P<category_slug>[-\w]+)/stores/$", StoresByCategory.as_view(), name="imly_stores_by_category"),
    url(r"^categories/(?P<category_slug>[-\w]+)/products/$", ProductsByCategory.as_view(), name="imly_products_by_category"),
)

urlpatterns += patterns('',
    
    url(r"^places/$", ListView.as_view(**location_info), name="imly_place_list" ),
    url(r"^places/(?P<place_slug>[-\w]+)/stores/$", StoresByPlace.as_view(), name="imly_stores_by_place"),
    url(r"^places/(?P<place_slug>[-\w]+)/products/$", "products_by_place", name="imly_products_by_place"),
    
)

urlpatterns += patterns('',
    url(r"^account/store/products/add/$", login_required(ProductCreate.as_view()), name="imly_product_add"),
    url(r"^account/store/products/(?P<pk>\d+)/edit$", login_required(ProductEdit.as_view()), name="imly_product_edit"),
    url(r"^account/store/products/(?P<pk>\d+)/delete/$", login_required(ProductDelete.as_view()), name="imly_product_delete"),
    url(r"^account/store/products/$", login_required(ProductsByAccount.as_view()), name="imly_store_products" ),
    
)
urlpatterns += patterns('',
    url(r"^shop/", include(shop.urls), name="imly_shop"),
    url(r"^shop/add/(?P<product_slug>[-\w]+)/$", "imly.views.stores.add_order", name="imly_add_order"),
    
)
