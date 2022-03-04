from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT,USER_AGENT
from ..utils import unquote_url


class Dogpile(SearchEngine):
    '''Seaches dogpile.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT,fakeagent=False):
        super(Dogpile, self).__init__(proxy, timeout)
        self._base_url = 'https://www.dogpile.com'
        if fakeagent:
            self.set_headers({'User-Agent': FAKE_USER_AGENT})
        else:
            self.set_headers({'User-Agent': USER_AGENT})
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a[class$=title]', 
            'title': 'a[class$=title]', 
            'text': {'tag':'span', 'index':-1}, 
            'links': 'div[class^=web-] div[class$=__result]', 
            'next': 'a.pagination__num--next'
        }
        return selectors[element]


    def _img_first_page(self):
        '''This is to return the first page of images'''
        url_str = u'{}/serp?qc=images&q={}'
        url = url_str.format(self._base_url, self._query)
        return {'url': url, 'data': None}


    def _first_page(self):
        '''Returns the initial page and query.'''
        url = u'{}/serp?q={}'.format(self._base_url, self._query)
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = (self._base_url + next_page) if next_page else None
        return {'url':url, 'data':None}

    def _get_text(self, tag, item='text'):
        '''Returns the text of search results items.'''
        selector = self._selectors('text')
        tag = tag.select(selector['tag'])[selector['index']]
        return self._get_tag_item(tag, 'text')

    def _get_images(self, soup):
        #all_lists=soup.findAll("ul",{"class":"dgControl_list"})
        returnlinks = []
        #dogpile's captcha is too stronk right now
        #for ul in all_lists:
        #    childlinks=ul.findChildren('a',{"class":"iusc"})
        #    for link in childlinks:
        #        linktopicture=ast.literal_eval(link.attrs['m'])['murl']
        #        returnlinks.append(linktopicture)
        return returnlinks

    
