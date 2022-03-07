from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT,FAKE_USER_AGENT,USER_AGENT


class Ask(SearchEngine):
    '''Searches ask.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT,fakeagent=False):
        super(Ask, self).__init__(proxy, timeout)
        self._base_url = 'https://uk.ask.com'
        if fakeagent:
            self.set_headers({'User-Agent':FAKE_USER_AGENT})
        else:
            self.set_headers({'User-Agent': USER_AGENT})
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.PartialSearchResults-item-title-link.result-link', 
            'title': 'a.PartialSearchResults-item-title-link.result-link', 
            'text': 'p.PartialSearchResults-item-abstract', 
            'links': 'div.PartialSearchResults-body div.PartialSearchResults-item', 
            'next': 'li.PartialWebPagination-next a[href]'
        }
        return selectors[element]

    def _img_first_page(self):
        #Ask does not have an image search feature. We will have it return an empty list.
        '''Returns the initial page and query.'''
        url_str = u'{}/web?o=0&l=dir&qo=serpSearchTopBox&q={}'
        url = url_str.format(self._base_url, self._query)
        return {'url':url, 'data':None}

    def _first_page(self):
        '''Returns the initial page and query.'''
        url_str = u'{}/web?o=0&l=dir&qo=serpSearchTopBox&q={}'
        url = url_str.format(self._base_url, self._query)
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        next_page = tags.select_one(self._selectors('next'))
        url = None
        if next_page:
            url = self._base_url + next_page['href']
        return {'url':url, 'data':None}

    def _get_images(self, soup):
        #there is no image search function, so have it return an empty list for compatibility.
        returnlinks = []

        return returnlinks