from django.conf.urls import patterns, include, url
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from imly.models import Product, Store, Category, Location


from imly.views.stores import StoreList, StoreCreate, StoreDetail, StoreEdit, StoresByCategory, StoresByPlace, StoreInfoDetail, OrderList, home_page
from imly.views.products import ProductReview, ProductList, ProductsByCategory, ProductCreate, ProductDelete, ProductDetail, ProductEdit, ProductsByAccount, coming_soon
from imly.views.profile import ProfileInfo,ProfileCreate,EditProfile,UserOrders
from imly.views.places import set_location

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
    "queryset" : Product.objects.is_approved().all(),
    "template_name" : "product_list.html"
}

store_info = {
    "queryset" : Store.objects.is_approved().all(),
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
    
    url(r"^$", home_page, name="imly_landing_page"),
    url(r"^index/$", home_page, name="imly_landing_page_index"), #same as above, sent this link to iq bootcamp, therefore dont remove for now
    url(r"^stores/$", StoreList.as_view(), name="imly_store_list"),
    url(r"^stores/(?P<slug>[-\w]+)/$", StoreDetail.as_view() , name="imly_store_detail"),
    url(r"^account/store/create/$", login_required(StoreCreate.as_view()), name ="imly_store_create"),
    url(r"^account/store/details", login_required(StoreInfoDetail.as_view()), name ="imly_store_info"),
    url(r"^account/my_profile/$",login_required(ProfileInfo.as_view()),name='imly_my_profile'),
    url(r"^account/create_profile/$",login_required(ProfileCreate.as_view()),name='imly_create_profile'),
    url(r"^account/edit_profile/(?P<pk>\d+)/$",login_required(EditProfile.as_view()),name='imly_profile_edit'),
    url(r"^account/user_orders/(?P<pk>\d+)/$",login_required(UserOrders.as_view()),name='imly_user_orders'),
    url(r"^account/store/edit/$", login_required(StoreEdit.as_view()), name="imly_store_edit"),
    url(r"^account/store/orders/$", login_required(OrderList.as_view()), name="imly_store_orders"),
    
    url(r"^coming_soon/$", coming_soon, name="imly_coming_soon"),
)

urlpatterns += patterns('',
    
    url(r"^products/$", ProductList.as_view(), name="imly_product_list"),
    url(r"^stores/(?P<store_slug>[-\w]+)/products/(?P<slug>[-\w]+)/$", ProductDetail.as_view(), name="imly_product_detail"),
    url(r"^review/$", ProductReview.as_view(), name="submit_product_review"),
    
)

urlpatterns += patterns('',
    
    #url(r"^categories/$", ListView.as_view(**category_info), name="imly_category_list" ),
    url(r"^categories/(?P<category_slug>[-\w]+)/stores/$", StoresByCategory.as_view(), name="imly_stores_by_category"),
    url(r"^categories/(?P<category_slug>[-\w]+)/products/$", ProductsByCategory.as_view(), name="imly_products_by_category"),
)

urlpatterns += patterns('',
    
    url(r"^set_location/(?P<place_slug>[-\w]+)$", set_location, name="imly_filter_by_place"),
    #url(r"^places/$", ListView.as_view(**location_info), name="imly_place_list" ),
    #url(r"^places/(?P<place_slug>[-\w]+)/stores/$", StoresByPlace.as_view(), name="imly_stores_by_place"),
    #url(r"^places/(?P<place_slug>[-\w]+)/products/$", "products_by_place", name="imly_products_by_place"),
    
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


