from bs4 import BeautifulSoup

from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT


class Startpage(SearchEngine):
    '''Searches startpage.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT): 
        super(Startpage, self).__init__(proxy, timeout)
        self._base_url = 'https://www.startpage.com'
        self.set_headers({'User-Agent':FAKE_USER_AGENT})
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.w-gl__result-url', 
            'title': 'a.w-gl__result-title h3', 
            'text': 'p.w-gl__description', 
            'links': 'section.w-gl div.w-gl__result', 
            'next': {'form':'form.pagination__form', 'text':'Next'},
            'search_form': 'form#search input[name]'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        response = self._get_page(self._base_url)
        tags = BeautifulSoup(response.html, "html.parser")
        selector = self._selectors('search_form')

        data = {
            i['name']: i.get('value', '') 
            for i in tags.select(selector)
        }
        data['query'] = self._query
        url = self._base_url + '/sp/search'
        return {'url':url, 'data':data}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        forms = [
            form 
            for form in tags.select(selector['form']) 
            if form.get_text(strip=True) == selector['text']
        ]
        url, data = None, None
        if forms:
            url = self._base_url + forms[0]['action']
            data = {
                i['name']:i.get('value', '') 
                for i in forms[0].select('input')
            }
        return {'url':url, 'data':data}
