from django.conf.urls import patterns, include, url
from .views import home, FBProductDetail, fb_add_order, fb_one_step_checkout
urlpatterns = patterns('',
    
    url(r"^$", home, name="facestore_landing_page"),
    url(r"^facebook/add/(?P<store_slug>[-\w]+)/(?P<product_slug>[-\w]+)/$", fb_add_order, name="fb_add_order"),
    url(r"^facebook/checkout/$", fb_one_step_checkout, name="fb_checkout"),
    url(r"^(?P<store_slug>[-\w]+)/(?P<slug>[-\w]+)/$", FBProductDetail.as_view(), name="fb_product_detail"),
    )