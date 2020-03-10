from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT


class Mojeek(SearchEngine):
    '''Searches mojeek.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Mojeek, self).__init__(proxy, timeout)
        self._base_url = 'https://www.mojeek.com'
        self.set_headers({'User-Agent':FAKE_USER_AGENT})
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.ob[href]', 
            'title': 'a.ob[href]', 
            'text': 'p.s', 
            'links': 'ul.results-standard > li', 
            'next': {'href':'div.pagination li a[href]', 'text':'Next'}
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url = u'{}/search?q={}'.format(self._base_url, self._query)
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

