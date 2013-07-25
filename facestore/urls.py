from django.conf.urls import patterns, include, url
from .views import home
urlpatterns = patterns('',
    
    url(r"^$", home, name="facestore_landing_page"),
    )