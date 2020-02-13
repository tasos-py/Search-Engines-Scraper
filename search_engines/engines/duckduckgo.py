from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT


class Duckduckgo(SearchEngine):
    '''Searches duckduckgo.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Duckduckgo, self).__init__(proxy, timeout)
        self._base_url = 'https://duckduckgo.com/html/'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.result__snippet', 
            'title': 'h2.result__title a', 
            'text': 'a.result__snippet', 
            'links': 'div.results div.result.results_links.results_links_deep.web-result', 
            'next': 'div.nav-link form input[name]'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        data = {'q':self._query, 'b':'', 'kl':'us-en'} 
        return {'url':self._base_url, 'data':data}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        inputs = tags.select(self._selectors('next'))
        url, data = None, None
        if inputs:
            data = {i['name']:i.get('value', '') for i in inputs}
            url = self._base_url
        return {'url':url, 'data':data}

