# Copyright 2007 Casey Durfee
#
# This file is part of Kochief.
# 
# Kochief is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Kochief is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Kochief.  If not, see <http://www.gnu.org/licenses/>.

from django.utils.translation import ugettext as _

SEARCH_CACHE_TIME = 6000    # in seconds
ITEMS_PER_PAGE = 10
MAX_FACET_TERMS_BASIC = 4    # how many facet terms display by default
MAX_FACET_TERMS_EXPANDED = 25 # how many facet terms display when you hit "show more"
LOCAL_LOGO_LOCATION = 'http://www.laurentian.ca/Laurentian.WCMSPortal/Inc/images/logo_laurentian.jpg' #image with 177 x 54 pixels
LOCAL_INSTITUTION_NAME = 'Colorado College Tutt Library'
# Horizon IPAC example
#OPAC_FULL_BIB_URL = "http://catalog.spl.org/ipac20/ipac.jsp?index=BIB&term=%(bib_num)s"
# Unicorn iBistro / iLink example
OPAC_FULL_BIB_URL = "http://sirsiweb.laurentian.ca/uhtbin/cgisirsi/x/x/x/57/5/?user_id=WEBSERVER&searchdata1=%s{%s}"
# LOCAL_ITEM_DISPLAY has two settings:
# 0 : Make item title a link to the detailed view in vendor catalog
# 1 : Make item title a link to the detailed view in kochief
LOCAL_ITEM_DISPLAY = 1

## FACETS has several settings.
# name = Display name on the opac
# code = solr field name
# search = field name to search by when clicked
# sort_by = whether you want the facets sorted by count. Values 
#     can be count, alpha, and reverse_alpha (for reverse alphabetical order)
FACETS = [
    { 
        'name': _('Name'), 
        'code': 'name_facet', 
        'search': 'name', 
        'sort_by': 'count', 
    }, 
    { 
        'name': _('Topic'), 
        'code': 'topic_facet', 
        'search': 'topic', 
        'sort_by': 'count', 
    },    
    { 
        'name': _('Genre'), 
        'code': 'genre', 
        'search': 'genre', 
        'sort_by': 'count', 
    },
    {
        'name': _('LC Subject Heading'), 
        'code': 'full_lc_subject', 
        'search': 'genre', 
        'sort_by': 'alpha', 
    },                           
    {
        'name': _('Call Number'),
        'code': 'lc_firstletter',
        'search': 'lc_firstletter',
        'sort_by': 'alpha',

    }, 
    { 
        'name': _('Language'), 
        'code': 'language', 
        'search': 'language', 
        'sort_by': 'count', 
    }, 
#    { 
#        'name': _('Year of Publication'), 
#        'code': 'pubyear', 
#        'search': 'pubyear', 
#        'sort_by': 'reverse_alpha', 
#    },
    { 
        'name': _('Format'), 
        'code': 'format', 
        'search': 'format', 
        'sort_by': 'count', 
    },                         
    { 
        'name': _('Place'), 
        'code': 'place', 
        'search': 'place', 
        'sort_by': 'count', 
    },    
    {
        'name': _('Dewey Range'), 
        'code': 'callnumlayerone', 
        'search': 'callnumlayerone', 
        'sort_by': 'alpha', 
    },
    { 
        'name': _('Dewey Range'), 
        'code': 'callnumlayertwo', 
        'search': 'callnumlayertwo', 
        'sort_by': 'alpha', 
    }, 
    { 
        'name': _('Availability'), 
        'code': 'availability', 
        'search': 'availability', 
        'sort_by': 'alpha', 
    },
    { 
        'name': _('Author'), 
        'code': 'author_exact',
        'search': 'author',
        'sort_by': 'alpha', 
    },
]

#items listed in the search dropdown box
SEARCH_INDEXES = [ {'name' : _('Anywhere'), 'index': 'text'},
                  {'name' : _('Author'), 'index': 'author'} , { 'name' : _('Title'), 'index' : 'title' },
                  {'name' : _('Subject'), 'index': 'subject'}, { 'name' : _('ISBN'), 'index' : 'isbn' },]

#items to be listed in the "Sort By:" Dropdown box
SORTS = [{ 'name' : _('Pub. Date (newest first)'), 'direction' : 'desc', 'field' : 'pubyear' },
         { 'name' : _('Pub. Date (oldest first)'), 'direction' : 'asc', 'field' : 'pubyear' },
         { 'name' : _('Author A-Z'), 'direction' : 'desc', 'field' : 'author_exact' },
         { 'name' : _('Title A-Z'), 'direction': 'desc', 'field' : 'full_title'},]

#Icons corresponding to item type
FORMAT_ICONS = {'Atlas' : '<img src="/site_media/static/img/silk/icons/map.png" alt="Atlas" />',
                'Book' : '<img src="/site_media/static/img/silk/icons/book.png" alt="Book" />',
                'CDROM' : '<img src="/site_media/static/img/silk/icons/cd.png" alt="CDROM" />',
                'Collection' : '<img src="/site_media/static/img/silk/icons/package.png" alt="Collection" />',
                'DVD Video' : '<img src="/site_media/static/img/silk/icons/dvd.png" alt="DVD Video" />',
                'Electronic' : '<img src="/site_media/static/img/silk/icons/server_lightning.png" alt="Electronic" />',
                'Journal' : '<img src="/site_media/static/img/silk/icons/newspaper.png" alt="Journal" />',
                'Manuscript' : '<img src="/site_media/static/img/silk/icons/script.png" alt="Manuscript" />',
                'Map' : '<img src="/site_media/static/img/silk/icons/map.png" alt="Map" />',
                'Microfilm' : '<img src="/site_media/static/img/silk/icons/film.png" alt="Microfilm" />',
                'Musical Score' : '<img src="/site_media/static/img/silk/icons/music.png" alt="Musical Score" />',
                'Music CD' : '<img src="/site_media/static/img/silk/icons/cd.png" alt="Music CD" />',
                'Music Sound Recordings' : '<img src="/site_media/static/img/silk/icons/sound.png" alt="Music Sound Recordings" />',
                'Photo' : '<img src="/site_media/static/img/silk/icons/photo.png" alt="Photo" />',
                'Poster' : '<img src="/site_media/static/img/silk/icons/image.png" alt="Poster" />',
                'Thesis' : '<img src="/site_media/static/img/silk/icons/report.png" alt="Thesis" />',
                'Video' : '<img src="/site_media/static/img/silk/icons/film.png" alt="Video" />',
                'VHS Video' : '<img src="/site_media/static/img/silk/icons/film.png" alt="VHS Video" />',
                }

#White-whale template tags
#CC_URL = 'http://www.coloradocollege.edu/test/library/'
CC_URL = 'http://www.coloradocollege.edu/library/xindex.dot'

