#
# Catalog settings fields
#
#
# (c) 2011 Colorado College 
__author__ = 'Jeremy Nelson'

# Facets for catalog view
FACETS = {'default': [
           {'label':'Access','facet_field':'location'},
           {'label':'Format','facet_field':'format'},
           {'label':'Topic','facet_field':'subject_topic_facet'},
           {'label':'Language','facet_field':'language_facet'},
           {'label':'Call Number','facet_field':'lc_alpha_facet','sort':'asc'},
           {'label':'Publication Year','facet_field':'pub_date'}]}

SOLR_URL = 'http://172.25.1.106:8984/solr/marc_catalog'
