__author__ = 'Jeremy Nelson'
import logging
from django.views.generic.simple import direct_to_template
from django.conf.urls.defaults import *

ARISTOTLE_PATTERNS = patterns("",
    url(r"^$", include("discovery.urls")),
    url(r"^about/",include("about.urls")),
    url(r"^catalog/",include("discovery.urls")),
    url(r"^etd/",include("etd.urls")),
    url(r"^grx/",include("grx.urls")),
    url(r"^marc/",include("marc.urls")),
    url(r"^vendors/iii/",include("vendors.iii.urls")))
