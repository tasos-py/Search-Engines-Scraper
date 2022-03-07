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

    def _img_first_page(self):
        '''This is to return the first page of images'''
        url_str = u'{}/aol/image?q={}'
        url = url_str.format(self._base_url, self._query)
        return {'url': url, 'data': None}

    def _first_page(self):
        '''Returns the initial page and query.'''
        url_str = u'{}/aol/search?q={}&ei=UTF-8&nojs=1'
        url = url_str.format(self._base_url, self._query)
        self._http_client.get(self._base_url)
        return {'url':url, 'data':None}

    def _get_images(self, soup):
        maindiv=soup.find('div',{'class':'sres-cntr'})
        li_children=maindiv.findChildren('li')
        extensions = ['.jpg', '.jpeg', '.png', '.gif']
        returnlinks=[]
        for li in li_children:
            if 'data' in li.attrs:
                broken_down_li_data=li.attrs['data'].split('"')
                for item in broken_down_li_data:
                    for extension in extensions:
                        if extension in item:
                            returnlinks.append(item.replace("\\",""))
        return returnlinks