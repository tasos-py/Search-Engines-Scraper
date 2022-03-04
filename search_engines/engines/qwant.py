from json import loads

from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT, USER_AGENT
from ..utils import unquote_url


class Qwant(SearchEngine):
    '''Searches qwant.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT,fakeagent=False):
        super(Qwant, self).__init__(proxy, timeout)
        self._base_url = u'https://api.qwant.com/v3/search/web?q={}&count=10&locale=en_US&offset={}&device=desktop&safesearch=1'
        self._offset = 0
        self._max_offset = 50
        self._base_image_url='https://www.qwant.com/?t=images'
        if fakeagent:
            self.set_headers({'User-Agent':FAKE_USER_AGENT})
        else:
            self.set_headers({'User-Agent': USER_AGENT})
        
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'url', 
            'title': 'title', 
            'text': 'desc', 
            'links': ['data', 'result', 'items', 'mainline']
        }
        return selectors[element]

    def _img_first_page(self):
        '''This is to return the first page of images'''
        url_str = u'{}?q={}'
        url = url_str.format(self._base_url, self._query)
        return {'url': url, 'data': None}

    def _first_page(self):
        '''Returns the initial page and query.'''
        url = self._base_url.format(self._query, self._offset)
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        self._offset += 10
        url = None
        status = loads(tags.get_text())['status']
        if status == 'success' and self._offset <= self._max_offset:
            url = self._base_url.format(self._query, self._offset)
        return {'url':url, 'data':None}

    def _get_url(self, tag, item='href'):
        '''Returns the URL of search results item.'''
        return unquote_url(tag.get(self._selectors('url'), u''))
    
    def _get_title(self, tag, item='text'):
        '''Returns the title of search results items.'''
        return tag.get(self._selectors('title'), u'')
    
    def _get_text(self, tag, item='text'):
        '''Returns the text of search results items.'''
        return tag.get(self._selectors('text'), u'')
    
    def _filter_results(self, soup):
        '''Processes and filters the search results.''' 
        tags = loads(soup.get_text())['data']['result']['items']['mainline']
        tags = [j for i in tags for j in i['items'] if i['type'] != u'ads']
        results = [self._item(l) for l in tags]

        if u'url' in self._filters:
            results = [l for l in results if self._query_in(l['link'])]
        if u'title' in self._filters:
            results = [l for l in results if self._query_in(l['title'])]
        if u'text' in self._filters:
            results = [l for l in results if self._query_in(l['text'])]
        if u'host' in self._filters:
            results = [l for l in results if self._query_in(utils.domain(l['link']))]
        return results

    #qwant also does similar to Google. They only provide the thumbnails until you click on them.
    #I may as well apply the same logic to both Qwant and Google then?
    def _get_images(self, soup):
        all_images=soup.findAll('img')
        returnlinks = []
        for image in all_images:
            if "http" in image.attrs['src']:
                returnlinks.append(image.attrs['src'])
        return returnlinks