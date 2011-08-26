# 
# catalog_extras.py -- Custom Django template tags
#
# 
__author__ = 'Jeremy Nelson'
import urllib2,logging
from django import template
import django.utils.simplejson as json
from django.utils.safestring import mark_safe
from vendors.iii.bots.iiibots import ItemBot
import vendors.iii.settings as ils_settings

register = template.Library()


def display_ill(record):
    """
    Displays an ill link if the item's status is Checked out
    """
    for item_id in record.get('item_ils_number'):
        item_bot = ItemBot(opac_url=ils_settings.OPAC_URL,item_id=item_id)
        status = item_bot.status()
        if status is not None:
            if item_bot.status().startswith('Due'):
                return mark_safe('''<a href="#" onclick="alert('ill tbd')">Request</a> <em>%s</em> through
   Prospector or Interlibrary Loan (ILL)</li>''' % record.get('title_display'))
    return ''

def display_reserve(record):
    """
    Generates a list item if item can be reserved
    """
    pass



def display_rows_options(num_result,row_values=[10,20,50,100]):
    """
    Generates options for pagination widget's row count
    select field.
    """ 
    output_html = ''
    for row in row_values:
        output_html += '<option value="%s"' % row
        if row == num_result:
            output_html +=' selected="selected" '
        output_html += '>%s</option>' % row
    return mark_safe(output_html)
        

def generate_page_count(solr_result):
    """
    Custom template tag generates page number result for
    pagination widget
    """
    start_location = solr_result.start
    total_docs = solr_result.numFound
    num_rows = len(solr_result.docs)
    if total_docs >= (num_rows + start_location):
        return mark_safe(num_rows + start_location)
    else:
        return mark_safe(total_docs)

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
    amazon_image_url = 'http://ec2.images-amazon.com/images/P/%s.01._PE00_SCMZZZZZZZ_.jpg'
    for isbn in isbn_list:
        try:
            amazon_image_url = amazon_image_url % isbn.strip()
        except:
            pass
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
    item_bot = ItemBot(opac_url=ils_settings.OPAC_URL,item_id=item_id)
    item_status = item_bot.status()
    if item_status is None:
        css_class = ''
    elif item_status.startswith('Due'):
        css_class = 'due-back'
    else:
        css_class = 'available'
    status_txt = '''<span class="%s">%s</span>''' % (css_class,item_status)
    return mark_safe(status_txt)    

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
    """Generates a list of boolean search HTML options for
    AND, AND NOT, OR
    """
    for row in ['AND','AND NOT','OR']:
        output_html += '<option value="%s">%s</option>' % (row,row.title())
    return mark_safe(output_html)


register.filter("display_ill",
                display_ill)
register.filter("display_reserve",
                display_reserve)
register.filter("display_rows_options",
                display_rows_options)
register.filter('generate_page_count',
                generate_page_count)
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


