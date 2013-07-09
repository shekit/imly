from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from imly.models import Product, Store, Category, Location
from imly.views.stores import OrderList, StoreList, StoreCreate, StoreDetail, StoreEdit, StoreInfoDetail, home_page, why_open_your_shop, contact_us, faqs, what_is_imly, wrong_location, status, update_store_order, no_city, not_in_city
from imly.views.products import SpecialList, ProductReview, ProductList, ProductCreate, ProductDelete, ProductDetail, ProductEdit, ProductsByAccount, coming_soon,sort_product,activate_product,special_event,unsubscribe_event
from imly.views.profile import ProfileInfo,ProfileCreate,EditProfile, ChefProfile, ProfileList
from imly.views.places import set_location, unset_location, set_city
from imly.views.orders import UserOrders, StoreOrders, update_store_orders_for_order,update_cart,change_quantity
from imly.views.tags import add_tag, remove_tag
from imly.sitemaps import all_sitemaps as sitemaps
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
    
    url(r"^$", home_page, name="imly_landing_page"),
    url(r"^give_us_tip/$", "imly.views.profile.give_us_tip",name="imly_give_us_tip"),
    url(r"^login-x/$", "imly.views.profile.modal_login", name="imly_modal_login"),
    url(r"^signup-x/$", "imly.views.profile.modal_signup", name="imly_modal_signup"),
    url(r"^why-join-imly/$", why_open_your_shop, name="why_open_your_shop"),
    url(r"^contact-us/$", contact_us, name="imly_contact_us"),
    url(r"^faqs/$", faqs, name="imly_faqs"),
    url(r"^what-is-imly/$", what_is_imly, name="what_is_imly"),
    url(r"^chefs/$", StoreList.as_view(), name="imly_store_list"),
    url(r"^profiles/$", ProfileList.as_view(), name="imly_profiles"),
    url(r"^profiles/(?P<slug>[-\w]+)/$", ChefProfile.as_view(), name="chef_profile"),
    url(r"^specials/(?P<slug>[-\w]+)/$", SpecialList.as_view(), name='imly_specials'),
    url(r"^account/store/create/$", login_required(StoreCreate.as_view()), name ="imly_store_create"),
    url(r"^account/store/details/$", login_required(StoreInfoDetail.as_view()), name ="imly_store_info"),
    url(r"^account/my-profile/$",login_required(ProfileInfo.as_view()),name='imly_my_profile'),
    url(r"^account/create-profile/$",login_required(ProfileCreate.as_view()),name='imly_create_profile'),
    url(r"^account/edit-profile/$",login_required(EditProfile.as_view()),name='imly_profile_edit'),
    url(r"^account/orders/(?P<pk>\d+)/$",login_required(UserOrders.as_view()),name='imly_user_orders'),
    url(r"^account/store/edit/$", login_required(StoreEdit.as_view()), name="imly_store_edit"),
    url(r"^account/store/orders/$", login_required(StoreOrders.as_view()), name="imly_store_orders"),
    url(r"^account/store/sort-product/$","imly.views.products.sort_product",name="imly_store_sort_product"),
    url(r"^coming-soon/$", coming_soon, name="imly_coming_soon"),
    url(r"^no-such-place/$", wrong_location, name="wrong_location"),
    url(r"^will-be-there-soon/$", no_city, name="imly_dont_see_city"),
    url(r"^not-in-city/$", not_in_city, name="not_in_city"),
    url(r"^special_event/(?P<event_slug>[-\w]+)/(?P<product_slug>[-\w]+)/$",special_event,name="imly_special_event"),
    url(r"^unsubscribe_event/(?P<event_slug>[-\w]+)/(?P<product_slug>[-\w]+)/$",unsubscribe_event,name="imly_unsubscribe_event"),
    
)

urlpatterns += patterns('',
    
    url(r"^set_location/$", set_location, name="imly_filter_by_place"),
    url(r"^unset_location/$", unset_location, name="unset_location"),
    url(r'^set_city/(?P<slug>[-\w]+)/$', set_city, name='imly_set_city'),
    url(r"^add-tag/(?P<slug>[-\w]+)/$", add_tag, name="add_tag"),
    url(r"^remove-tag/(?P<slug>[-\w]+)/$", remove_tag, name="remove_tag"),
    #url(r"^places/$", ListView.as_view(**location_info), name="imly_place_list" ),
    #url(r"^places/(?P<place_slug>[-\w]+)/stores/$", StoresByPlace.as_view(), name="imly_stores_by_place"),
    #url(r"^places/(?P<place_slug>[-\w]+)/products/$", "products_by_place", name="imly_products_by_place"),
    
)


urlpatterns += patterns('',
    
    url(r"^food/$", ProductList.as_view(), name="imly_product_list"),
    url(r"^review/$", ProductReview.as_view(), name="submit_product_review"),
    url(r"^(?P<slug>[-\w]+)/$", StoreDetail.as_view() , name="imly_store_detail"),
    url(r"^account/store/status/$", "imly.views.stores.status" , name="imly_store_status"),
    
    
    
)

urlpatterns += patterns('',
    
    #url(r"^categories/$", ListView.as_view(**category_info), name="imly_category_list" ),
    url(r"^categories/(?P<category_slug>[-\w]+)/chefs/$", StoreList.as_view(), name="imly_stores_by_category"),
    url(r"^categories/(?P<category_slug>[-\w]+)/food/$", ProductList.as_view(), name="imly_products_by_category"),
)


urlpatterns += patterns('',
    url(r"^account/store/products/add/$", login_required(ProductCreate.as_view()), name="imly_product_add"),
    url(r"^account/store/products/(?P<pk>\d+)/edit$", login_required(ProductEdit.as_view()), name="imly_product_edit"),
    #url(r"^account/store/products/(?P<product_id>\d+)/delete/$", "imly.views.products.delete_product", name="imly_product_delete"),
    url(r"^account/store/products/(?P<pk>\d+)/delete/$", login_required(ProductDelete.as_view()), name="imly_product_delete"),
    url(r"^account/store/products/(?P<product_id>\d+)/activate/$", "imly.views.products.activate_product", name="imly_product_activate"),
    url(r"^account/store/products/$", login_required(ProductsByAccount.as_view()), name="imly_store_products" ),
    
)
urlpatterns += patterns('',
    url(r"^shop/", include(shop.urls), name="imly_shop"),
    url(r"^shop/add/(?P<store_slug>[-\w]+)/(?P<product_slug>[-\w]+)/$", "imly.views.stores.add_order", name="imly_add_order"),
    
)

urlpatterns += patterns('',
    url(r'^storeorder$', update_store_order, name='update_store_order'),
    url(r'^order/(?P<pk>\d+)/update-store-orders/$', update_store_orders_for_order, name='update_store_orders_for_order'),
    url(r'^orderitem/remove/$',update_cart,name='update_cart'),
    url(r'^orderitem/change_quantity/(?P<change>up|down)/$',change_quantity,name='change_quantity'),
    url(r'^sitemap.xml$', 'django.contrib.sitemaps.views.index', {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    url(r"^(?P<store_slug>[-\w]+)/(?P<slug>[-\w]+)/$", ProductDetail.as_view(), name="imly_product_detail"),
)
