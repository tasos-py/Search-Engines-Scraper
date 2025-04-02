from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT


class Duckduckgo(SearchEngine):
    '''Searches duckduckgo.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Duckduckgo, self).__init__(proxy, timeout)
        self._base_url = 'https://html.duckduckgo.com/html/'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.result__snippet', 
            'title': 'h2.result__title a', 
            'text': 'a.result__snippet', 
            'links': 'div.results div.result.results_links.results_links_deep.web-result', 
            'next': {'forms':'div.nav-link > form', 'inputs':'input[name]'}
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        data = {'q':self._query, 'b':'', 'kl':'us-en'} 
        return {'url':self._base_url, 'data':data}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        forms = tags.select(selector['forms'])
        url, data = None, None

        if forms:
            form = forms[-1]
            data = {i['name']:i.get('value', '') for i in form.select(selector['inputs'])}
            url = self._base_url
        return {'url':url, 'data':data}
