from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT


class Brave(SearchEngine):
    '''Searches brave.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Brave, self).__init__(proxy, timeout)
        self._base_url = 'https://search.brave.com'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.result-header[href]', 
            'title': 'a.result-header[href] span.snippet-title', 
            'text': 'div.snippet-content', 
            'links': 'div#results div[data-loc="main"]', 
            'next': {'tag':'div#pagination a[href]', 'text':'Next', 'skip':'disabled'}
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url_str = u'{}/search?q={}&source=web'
        url = url_str.format(self._base_url, self._query)
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = [
            tag for tag in tags.select(selector['tag']) 
            if tag.get_text().strip() == selector['text'] and selector['skip'] not in tag['class']
        ]
        url = None
        if next_page:
            url = self._base_url + next_page[0]['href']
        return {'url':url, 'data':None}

