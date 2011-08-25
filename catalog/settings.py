#
# Catalog settings fields
#
#
# (c) 2011 Colorado College 
__author__ = 'Jeremy Nelson'

# Facets for catalog view
FACETS = {'default': [
           {'label':'Access','facet_field':'access'},
           {'label':'Format','facet_field':'format'},
           {'label':'Topic','facet_field':'subject_topic_facet'},
           {'label':'Location','facet_field':'location'},
           {'label':'Language','facet_field':'language_facet'},
           {'label':'Call Number','facet_field':'lc_1letter_facet','sort':'asc'},
           {'label':'Publication Year','facet_field':'pub_date'},
           {'label':'Era','facet_field':'subject_era_facet'},
           {'label':'Geographic location','facet_field':'subject_geo_facet'}]}

SOLR_URL = 'http://172.25.1.106:8984/solr/marc_catalog'
SOLR_CACHE = 'catalog/solr_cache'
#SOLR_URL = 'http://0.0.0.0:8984/solr/marc_catalog'
