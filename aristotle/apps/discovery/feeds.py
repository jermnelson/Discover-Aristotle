"""
  feeds.py -- Aristotle Discovery Feeds
"""
import sunburnt
from django.conf import settings
from django.http import HttpRequest
from django.contrib.syndication.views import Feed


class SavedRecordsFeed(Feed):
    """
    SavedRecordsFeed creates an RSS feed based on the current
    values of the user's item carts stored in the session variables.
    """
    title = 'Aristotle Saved Record Feed'
    link = '/catalog/cart/feed'
    description = 'Saved Records from Aristotle'
 
    def items(self):
        all_items = []
        solr_server = sunburnt.SolrInterface(settings.SOLR_URL)
        #! DOESN"T WORK IN THIS VERSION DJANGO!!
        if self.request.session.has_key('item_cart'):
            item_cart = self.request.session['item_cart']
            for doc_id in item_cart:
                solr_response = solr_server.search(q='id:%s' % doc_id)
                if solr_response.result.numFound > 0:
                    all_items.append(solr_response.result.doc[0])

    def item_description(self,item):
        desc = ''
        if item.has_key('author'):
            desc += 'Author: %s' % item['author']
        if item.has_key('callnum'):
            desc += 'Call number: %s' % item['callnum']
        if item.has_key('format'):
            desc += 'Format: %s' % item['format']
        if item.has_key('url'):
            for url in item['url']:
                desc += 'URL: %s' % url
        return desc

    def item_title(self,item):
        if item.has_key('full_title'):
            return item['full_title']
        else:  
            return None
                    
