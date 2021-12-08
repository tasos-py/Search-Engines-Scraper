import aiohttp
from collections import namedtuple

from aiohttp_socks import ProxyConnector

from .config import TIMEOUT, PROXY, USER_AGENT
from . import utils as utl


class HttpClient(object):
    '''Performs HTTP requests. A `aiohttp` wrapper, essentialy'''
    def __init__(self, timeout=TIMEOUT, proxy=PROXY):
        if proxy:
            connector = ProxyConnector.from_url(proxy)
            self.session = aiohttp.ClientSession(connector=connector)
        else:
            self.session = aiohttp.ClientSession()

        self.headers = {
            'User-Agent': USER_AGENT,
            'Accept-Language': 'en-GB,en;q=0.5',
        }

        self.timeout = timeout
        self.response = namedtuple('response', ['http', 'html'])

    async def close(self):
        await self.session.close()

    async def get(self, page):
        '''Submits a HTTP GET request.'''
        page = self._quote(page)
        try:
            req = await self.session.get(page, headers=self.headers, timeout=self.timeout)
            text = await req.text()
            self.headers['Referer'] = page
        except aiohttp.client_exception.ClientError as e:
            return self.response(http=0, html=e.__doc__)
        return self.response(http=req.status, html=text)
    
    async def post(self, page, data):
        '''Submits a HTTP POST request.'''
        page = self._quote(page)
        try:
            req = await self.session.post(page, data=data, headers=self.headers, timeout=self.timeout)
            text = await req.text()
            self.headers['Referer'] = page
        except aiohttp.client_exception.ClientError as e:
            return self.response(http=0, html=e.__doc__)
        return self.response(http=req.status, html=text)
    
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

