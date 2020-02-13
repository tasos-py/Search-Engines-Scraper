from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT


class Startpage(SearchEngine):
    '''Searches startpage.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT): 
        super(Startpage, self).__init__(proxy, timeout)
        self._base_url = 'https://www.startpage.com'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.w-gl__result-url', 
            'title': 'a.w-gl__result-title h3', 
            'text': 'p.w-gl__description', 
            'links': 'section.w-gl.w-gl--default div.w-gl__result', 
            'next': {'form':'form.pagination__form', 'text':'Next'} 
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        data = { 
            'query':self._query, 'cat':'web', 'cmd':'process_search', 
            'language':'english_uk', 'engine0':'v1all', 
            'pg':0, 'abp':-1
        }
        url = self._base_url + '/sp/search'
        return {'url':url, 'data':data}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        forms = [
            form for form in tags.select(selector['form']) 
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

