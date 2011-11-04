# Example Django local settings for Aristotle project.
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'
BASE_URL = r'/'
DEBUG = True
TEMPLATE_DEBUG = DEBUG
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

DEV_ENV = True

# Aristotle Development Applications
ARISTOTLE_APPS = ["about",
                  "discovery",
                  "etd",
                  "grx",
                  "marc",
                  "vendors.bioheritage",
                  "vendors.iii"]

ARISTOTLE_TEMPLATE_DIRS = [os.path.join(PROJECT_ROOT,
                                        "templates/discovery/snippets"),
                           os.path.join(PROJECT_ROOT,
                                        "templates/vendors/whitewhale"),
                           os.path.join(PROJECT_ROOT,
                                        "apps/etd/templates/etd"),
                           os.path.join(PROJECT_ROOT,"templates/grx"),
                           os.path.join(PROJECT_ROOT,"templates/marc"),
]
 
ADMINS = (
     ('ADMIN NAME', 'xx@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(BASE_DIR,'dev.db'),  # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'PLEASE SET THIS VALUE'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

ugettext = lambda s: s

LANGUAGES = (
    ('fr', ugettext('French')),
    ('en', ugettext('English')),
    ('es', ugettext('Spanish')),
)

SESSION_EXPIRE_AT_BROWSER_CLOS = True
SOLR_URL = 'http://0.0.0.0:8984/solr/marc_catalog/'
GRX_SOLR_URL = 'http://0.0.0.0:8984/solr/grx/'
GRX_SOLR_DIR = '/usr/local/solr_server/multicore/grx/'
SOLR_DIR = '/usr/local/solr_server/multicore/marc_catalog/'
ILS = 'III'
MAJAX_URL = ''
CATALOG_RECORD_URL = ''
MAX_FACET_TERMS_BASIC = 4
MAX_FACET_TERMS_EXPANDED = 25
INDEX_FACET_TERMS = 20
INDEX_FACETS = [
    {
        'name': ugettext('Access'),
        'field': 'access',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Format'),
        'field': 'format',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Topics'),
        'field': 'subject',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Location'),
        'field': 'location',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Language'),
        'field': 'language',
        'sort_by_count': True,
    },
    {
        'name': ugettext('Call Number'),
        'field': 'lc_firstletter',
        'sort_by_count': False,
    },
    {
        'name': ugettext('Publication Year'),
        'field': 'pubyear',
        'sort_by_count': False,
    },
    {
        'name': ugettext('Geographic Location'),
        'field': 'place',
        'sort_by_count': True,
    },
]
FACETS = INDEX_FACETS

ITEMS_PER_PAGE = 20
SORTS = (
    (ugettext('newest'), 'year desc'),
    (ugettext('oldest'), 'year asc'),
    (ugettext('relevance'), ''),
    (ugettext('title'), 'title_sort asc'),
)
SEARCH_CACHE_TIME = 6000
LOCALNS = BASE_URL + 'r/'

# Email settings
EMAIL_HOST = 'NEEDS VALUE'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'test@example.com'
EMAIL_HOST_PASSWORD = 'xxxxx'
EMAIL_USE_TLS = True

PROSPECTOR_URL = 'http://prospector.coalliance.org/search/z?9cocp+%s&backlink=http://discovery.coloradocollege.edu/catalog/record/%s'
ILS_HOLD_URL = 'https://tiger.coloradocollege.edu/search~S5/.%s/.%s/1,1,1,B/request~%s'
ILS_PATRON_URL = 'https://tiger.coloradocollege.edu:54620/PATRONAPI/%s/dump' 
# Fedora Repository settings
FEDORA_ETDCMODEL = ''
FEDORA_ROOT = ''
FEDORA_PIDSPACE = ''
FEDORA_USER = ''
FEDORA_PASSWORD = ''
