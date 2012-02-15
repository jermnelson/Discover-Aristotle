from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()


import logging




try:
    from local_urls import *
    urlpatterns = ARISTOTLE_PATTERNS
except ImportError:
    urlpatterns = patterns("",
        url(r"^$", include("discovery.urls")))

urlpatterns += patterns("",
    url(r"^admin/", include(admin.site.urls)),
    url(r"^vendors/iii/",include("vendors.iii.urls")),
)

## @@@ for now, we'll use friends_app to glue this stuff together


