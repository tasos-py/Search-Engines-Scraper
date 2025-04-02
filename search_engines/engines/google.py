from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT
from ..utils import unquote_url, quote_url
from bs4 import BeautifulSoup


class Google(SearchEngine):
    '''Searches google.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(Google, self).__init__(proxy, timeout)
        self._base_url = 'https://www.google.com'
        self._delay = (2, 6)
        
        self.set_headers({'User-Agent':'Lynx/2.8.6rel.5 libwww-FM/2.14'})

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'div > a[href]', 
            'title': 'a', 
            'text': 'table',
            'links': 'item', 
            'next': 'footer a[href][aria-label="Next page"]'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url = u'{}/search?q={}'.format(self._base_url, quote_url(self._query, ''))
        page = self._get_page(url)
        self._check_consent(page)
        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        tag = tags.select('table a[href*="start="]')[-1]
        next_page = self._get_tag_item(tag, 'href')
        url = None

        if next_page:
            url = self._base_url + next_page
        return {'url':url, 'data':None}

    def _get_url(self, tag, item='href'):
        '''Returns the URL of search results item.'''
        selector = self._selectors('url')
        url = self._get_tag_item(tag.select_one(selector), item)

        if url.startswith(u'/url?q='):
            url = url.replace(u'/url?q=', u'').split(u'&sa=')[0]
        return unquote_url(url)

    def _get_text(self, tag, item='text'):
        '''Returns the text of search results items.'''
        tag = tag.select_one(self._selectors('text'))
        return tag.text if tag else ''

    def _check_consent(self, page):
        '''Checks if cookies consent is required'''
        url = 'https://consent.google.com/save'
        bs = BeautifulSoup(page.html, "html.parser")
        consent_form = bs.select('form[action="{}"] input[name]'.format(url))
        if consent_form:
            data = {i['name']:i.get('value') for i in consent_form if i['name'] not in ['set_sc', 'set_aps']}
            page = self._get_page(url, data)
        return page
    
    def _filter_results(self, soup):
        '''Processes and filters the search results.''' 
        tags = [i.find_parent('div').find_parent('div') for i in soup.select('div a[href^="/url?q="]')][:-1]
        soup = BeautifulSoup(''.join('<item>' + str(i) + '</item>' for i in tags), "html.parser")
        return super(Google, self)._filter_results(soup)
