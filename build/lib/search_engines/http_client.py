import requests
from collections import namedtuple

from .config import TIMEOUT, PROXY, USER_AGENT
from . import utils as utl


class HttpClient(object):
    '''Performs HTTP requests. A `requests` wrapper, essentialy'''
    def __init__(self, timeout=TIMEOUT, proxy=PROXY):
        self.session = requests.session()
        self.session.proxies = self._set_proxy(proxy)
        self.session.headers['User-Agent'] = USER_AGENT
        self.session.headers['Accept-Language'] = 'en-GB,en;q=0.5'

        self.timeout = timeout
        self.response = namedtuple('response', ['http', 'html'])

    def get(self, page):
        '''Submits a HTTP GET request.'''
        page = self._quote(page)
        try:
            req = self.session.get(page, timeout=self.timeout)
            self.session.headers['Referer'] = page
        except requests.exceptions.RequestException as e:
            return self.response(http=0, html=e.__doc__)
        return self.response(http=req.status_code, html=req.text)
    
    def post(self, page, data):
        '''Submits a HTTP POST request.'''
        page = self._quote(page)
        try:
            req = self.session.post(page, data, timeout=self.timeout)
            self.session.headers['Referer'] = page
        except requests.exceptions.RequestException as e:
            return self.response(http=0, html=e.__doc__)
        return self.response(http=req.status_code, html=req.text)
    
    def _quote(self, url):
        '''URL-encodes URLs.'''
        if utl.decode_bytes(utl.unquote_url(url)) == utl.decode_bytes(url):
            url = utl.quote_url(url)
        return url
    
    def _set_proxy(self, proxy):
        '''Returns HTTP or SOCKS proxies dictionary.'''
        if proxy:
            if not utl.is_url(proxy):
                raise ValueError('Invalid proxy format!')
            proxy = {'http':proxy, 'https':proxy}
        return proxy

