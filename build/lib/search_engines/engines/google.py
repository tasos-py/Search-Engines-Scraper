from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT
from ..utils import unquote_url, quote_url
from .. import output as out
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs


class Google(SearchEngine):
    '''Searches google.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT, before=None, after=None):
        super(Google, self).__init__(proxy, timeout)
        self._base_url = 'https://www.google.com'
        self._delay = (2, 6)
        self.before = before
        self.after = after
        
        self.set_headers({'User-Agent':FAKE_USER_AGENT})

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a[href]', 
            'title': 'a h3', 
            'text': 'div',
            'links': 'div#main > div', 
            'next': 'footer a[href][aria-label="Next page"]'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url = u'{}/search?q={}'.format(self._base_url, quote_url(self._query, ''))
        response = self._get_page(url)
        bs = BeautifulSoup(response.html, "html.parser")
        
        noscript_link = bs.select_one('noscript a')
        if noscript_link and 'href' in noscript_link.attrs:
            url = noscript_link['href']
            url = u'{}/search?{}'.format(self._base_url, url)
        else:
            # Look for any 'a' tag with a 'data-ved' attribute
            data_ved_link = bs.select_one('a[data-ved]')
            if data_ved_link and 'href' in data_ved_link.attrs:
                url = data_ved_link['href']
                if url.startswith('/url?'):
                    # Extract the actual URL from Google's redirect URL
                    parsed_url = urlparse(url)
                    query_params = parse_qs(parsed_url.query)
                    if 'q' in query_params:
                        url = query_params['q'][0]
                else:
                    url = u'{}{}'.format(self._base_url, url)
            else:
                msg = "Warning: Could not find expected 'noscript a' element or any 'a' tag with 'data-ved'. Using original URL."
                out.console(msg, level=out.Level.error)
        
        response = self._get_page(url)
        bs = BeautifulSoup(response.html, "html.parser")

        inputs = {i['name']:i.get('value') for i in bs.select('form input[name]') if i['name'] != 'btnI'}
        inputs['q'] = quote_url(self._query, '')
        inputs['q'] = inputs['q']+f'+after:{self.after}+before:{self.before}'
        url = u'{}/search?{}'.format(self._base_url, '&'.join([k + '=' + (v or '') for k,v in inputs.items()]))
        print("!!! NEW URL", url)
        # if self.after and self.before:
        #     url = url+f'+after:{self.after}+before:{self.before}'
        # print("!!! NEW URL", url)

        return {'url':url, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        #tags = self._check_consent(tags)
        tag = tags.select_one(self._selectors('next'))
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
        return '\n'.join(list(tag.stripped_strings)[2:]) if tag else ''

    def _check_consent(self, page):
        '''Checks if cookies consent is required'''
        url = 'https://consent.google.com/save'
        bs = BeautifulSoup(page.html, "html.parser")
        consent_form = bs.select('form[action="{}"] input[name]'.format(url))
        if consent_form:
            data = {i['name']:i.get('value') for i in consent_form if i['name'] not in ['set_sc', 'set_aps']}
            page = self._get_page(url, data)
        return page

    def _get_page(self, page, data=None):
        '''Gets pagination links.'''
        page = super(Google, self)._get_page(page, data)
        page = self._check_consent(page)
        return page
