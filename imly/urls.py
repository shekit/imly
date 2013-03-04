from django.conf.urls import patterns, include, url
from django.views.generic import ListView
from imly.models import *

from imly.views.stores import StoresByCategory
from imly.views.products import ProductsByCategory

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
    #url(r"^stores/(?P<store_slug>[-\w]+)/$", "store_detail", name="imly_store_detail"),
)

urlpatterns += patterns('',
    
    url(r"^products/$", ListView.as_view(**product_info), product_info, name="imly_product_list"),
    #url(r"^stores/(?P<store_slug>[-\w]+)/products/(?P<product_slug>[-\w]+)/$", "product_detail", name="imly_product_detail"),
    
)

urlpatterns += patterns('',
    
    url(r"^categories/$", ListView.as_view(**category_info), name="imly_category_list" ),
    url(r"^categories/(?P<category_slug>[-\w]+)/stores/$", StoresByCategory.as_view(), name="imly_stores_by_category"),
    url(r"^categories/(?P<category_slug>[-\w]+)/products/$", ProductsByCategory.as_view(), name="imly_products_by_category"),
)

urlpatterns += patterns('',
    
    url(r"^places/$", ListView.as_view(**location_info), name="imly_place_list" ),
#    url(r"^places/(?P<place_slug>[-\w]+)/stores/$", "stores_by_place", name="imly_stores_by_place"),
#    url(r"^places/(?P<place_slug>[-\w]+)/products/$", "products_by_place", name="imly_products_by_place"),
    
)