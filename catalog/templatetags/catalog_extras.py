# 
# catalog_extras.py -- Custom Django template tags
#
# 
__author__ = 'Jeremy Nelson'
import urllib2,logging
from django import template
import django.utils.simplejson as json
from django.utils.safestring import mark_safe

register = template.Library()

def generate_search_filter(param):
    """
    Custom template tag to generate list item for search-filter
    html list.
    """
    term_list,output_html = [],''
    if param[0] == 'q':
        raw_query = param[1]
        if raw_query.count('AND') > 0: # For AND boolean operator
            term_list = [(v,'q') for v in raw_query.split('AND')]
        elif raw_query.count('OR') > 0: # For OR boolean operator
            term_list = [(v,'q') for v in raw_query.split('OR')]
        else:
            term_list.append((raw_query,'q'))
    elif param[0] == 'fq':
        raw_facets = param[1]
        if type(raw_facets) == list:
            for facet in raw_facets:
                logging.error("FACET is %s" % facet)
                name,value = facet.split(":")
                term_list.append((facet,'fq'))
        else:
            name,value = raw_facets.split(":")
            term_list.append((raw_facets,'fq'))

    for i,term in enumerate(term_list):
        #term = (term[0].replace('\\','').strip(),term[1]) # Strip out trailing forward slash
        li_id = '%st%s' % (i,term[1])
        output_html += '''<li id="%s"><a href="#" onclick="RemoveTerm('%s')">%s</a>''' % (li_id,li_id,term[0])
        output_html += '<input type="hidden" value="%s" name="%s" ></li>' % term
    return mark_safe(output_html)


def get_cover_thumbnail_url(isbn_list):
    """
    Custom method queries multiple web services for a thumbnail image,
    returns a matched URL using isbn number
    """
    if isbn_list is None:
        logging.error("INPUT ISBN_LIST IS NONE")
        return None
    logging.error(isbn_list)
    amazon_image_url = 'http://ec2.images-amazon.com/images/P/%s.01._PE00_SCMZZZZZZZ_.jpg'
    for isbn in isbn_list:
        logging.error("TYPE is %s" % type(isbn))
        try:
            amazon_image_url = amazon_image_url % isbn.strip()
        except:
            pass
        logging.error(amazon_image_url)
        #google_book_api_url = 'https://www.googleapis.com/books/v1/volumes?q=isbn:%s' % isbn
        #try:
        #    raw_json = urllib2.urlopen(google_book_api_url).read()
        #    if book_json['totalItems'] > 0:
        #        if book_json['items'][0]['volumeInfo'].has_key('imageLinks'):
        #            return mark_safe(book_json['items'][0]['volumeInfo']['imageLinks']['thumbnail'])
        #except:
        #    logging.error("Could not retrieve url for %s" % isbn)
        #    return None
    return mark_safe(amazon_image_url)

def get_item_status(item_id):
    """
    Method connects to ILS and retrieves the current circulation status
    of a an item.
    """
    status_txt = None
    return marc_safe(status_txt)    

def search_field_options(output_html):
    """
    Generates a list of field search options
    """
    field_types = [('keyword','Any Field'),
                   ('author','Author'),
                   ('title','Title'),
                   ('subject','Subject')]
    for row in field_types:
        output_html += '<option value="%s">%s</option>' % row
    return mark_safe(output_html)

def search_operator_options(output_html):
    """
    Generates a list of boolean search options AND, AND NOT, OR
    """
    for row in ['AND','AND NOT','OR']:
        output_html += '<option value="%s">%s</option>' % (row,row.title())
    return mark_safe(output_html)



register.filter('generate_search_filter',
                generate_search_filter)
register.filter('get_cover_image',
                get_cover_thumbnail_url)
register.filter('get_item_status',
                get_item_status)
register.filter('search_field_options',
                search_field_options)
register.filter('search_operator_options',
                search_operator_options)


