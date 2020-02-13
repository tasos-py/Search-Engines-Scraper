from ..engine import SearchEngine
from ..config import TOR, TIMEOUT
from .. import output as out


class Torch(SearchEngine):
    '''Uses torch search engine. Requires TOR proxy.'''
    def __init__(self, proxy=TOR, timeout=TIMEOUT):
        super(Torch, self).__init__(proxy, timeout)
        self._base_url = u'http://xmh57jrzrnw6insl.onion/4a1f6b371c/search.cgi'
        if not proxy:
            out.console('Torch requires TOR proxy!', level=out.Level.warning)
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'dt a[href]', 
            'title': 'dt a[href]', 
            'text': 'dd table tr td small', 
            'links': 'body dl', 
            'next': {'href':'table tr td a[href]', 'text':'Next >>'}
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url_str = u'{}?q={}&cmd=Search!&ps=50'
        url = url_str.format(self._base_url, self._query)
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = [
            i['href'] for i in tags.select(selector['href']) 
            if i.text == selector['text']
        ]
        url = (self._base_url + next_page[0]) if next_page else None
        return {'url':url, 'data':None}

