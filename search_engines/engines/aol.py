from .yahoo import Yahoo
from ..config import PROXY, TIMEOUT,FAKE_USER_AGENT,USER_AGENT


class Aol(Yahoo):
    '''Seaches aol.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT,fakeagent=False):
        super(Aol, self).__init__(proxy, timeout)
        self._base_url = u'https://search.aol.com'
        if fakeagent:
            self.set_headers({'User-Agent':FAKE_USER_AGENT})
        else:
            self.set_headers({'User-Agent': USER_AGENT})

    def _first_page(self):
        '''Returns the initial page and query.'''
        url_str = u'{}/aol/search?q={}&ei=UTF-8&nojs=1'
        url = url_str.format(self._base_url, self._query)
        self._http_client.get(self._base_url)
        return {'url':url, 'data':None}

