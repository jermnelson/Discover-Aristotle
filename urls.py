from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r"^$",include('catalog.urls')),
    url(r"^catalog",include('catalog.urls')),
    url(r"^etd",include('etd.urls')),
#    url(r"^grx",include('grx.urls')),
    # Examples:
    # url(r'^$', 'aristotle.views.home', name='home'),
    # url(r'^aristotle/', include('aristotle.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
