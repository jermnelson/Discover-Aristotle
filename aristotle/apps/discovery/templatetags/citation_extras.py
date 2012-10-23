"""
 citation_extras.py -- Django Template Tag Library for Common Bibilographic Citation
"""
__author__ = 'Jeremy Nelson'
import re,logging
from django import template
from django.utils.safestring import mark_safe
register = template.Library()

DATE_RE = re.compile(r'\(*(\d+)\s*-*(d*)\)*')
SUFFIX_LIST = ['JR','SR','I','II','III','IV']

def separate_author(raw_author):
   """Takes Solr author string in format of family name, given name middle names
   and returns a dict of values for use by different citation styles

   :param raw_author: Raw author string usually in the format last name, given
                      name, and middle names
   :rtype: Dictionary of values with given, family, middle, and suffix keys
   """
   author = {}
   author_list = raw_author.split(",")
   # Assumes the first list item is the family name
   author['family'] = author_list[0]
   if len(author_list) > 1:
       # If second list item is present assume it is the given name
       author['given'] = author_list[1].strip()
       # Checks to see if last item is a suffix or date
       last_item = author_list[-1]
       if author['given'] == last_item.strip() or DATE_RE.search(last_item):
           pass
       elif SUFFIX_LIST.count(last_item):
           author['suffix'] = last_item.strip()
       else:
           if len(author_list) > 2:
               author['middle'] = []
               for name in author_list[2:]:
                   author['middle'].append(name.strip())
   return author

def apa_name(author):
    """Generates family name, given name first initial following APA
    format for author and editor in citation.

    :param author: Dictionary of given, family, middle, and suffix name
                   values
    :rtype: String of name in APA format
    """
    author = separate_author(author)
    output = author['family']
    if author.has_key('given'):
        output += ', %s.' % author['given'][0].upper()
    if author.has_key('middle'):
        for name in author['middle']:
            if len(name) > 0:
                output += ' %s.' % name[0].upper()
    return mark_safe(output)

def chicago_first_author(author):
    """Generates family name, given name first initial, cheats
    and uses apa_name function.


    :param author: Dictionary of given, family, middle, and suffix name
                   values
    :rtype: String of name in Chicago format
    """
    return apa_name(author)

def chicago_name(author):
    """Generates given name middle initials family name for
    additional authors in Chicago citation format.

    :param author: Dictionary of given, family, middle, and suffix name
                   values
    :rtype: String of name in Chicago format
    """
    author = separate_author(author)
    output = str()
    if author.has_key('given'):
        output += "%s " % author['given']
    if author.has_key('middle'):
        for name in author['middle']:
            output += '%s. ' % name[0].upper() 
    output += author['family']
    return mark_safe(output)
    
def mla_name(author):
    """Generates family name, given name, first initial for 
    MLA format.

    :param author: Dictionary of given, family, middle, and suffix name
                   values
    :rtype: String of name in MLA format
    """
    author = separate_author(author)
    output = author['family']
    if author.has_key('given'):
        output += ', %s' % author['given']
    if author.has_key('middle'):
        for name in author['middle']:
            output += '%s. ' % name
    if output[-1] != '.':
        output += '.'
    return mark_safe(output)


register.filter('apa_name',apa_name)
register.filter('chicago_first_author',chicago_first_author)
register.filter('chicago_name',chicago_name)
register.filter('mla_name',mla_name)
