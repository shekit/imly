from django.conf.urls import patterns, include, url
from django.views.generic.base import TemplateView
from imly_project import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'imly_project.views.home', name='home'),
    # url(r'^imly_project/', include('imly_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^nimda/', include(admin.site.urls)),
    #url(r'^community/', include('forum.urls')),
    url(r'^tracking/', include('tracking.urls')),
    url(r'^facestore/', include('facestore.urls')),
    url(r"", include("allauth.urls")),
    url(r"", include("imly.urls")),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
