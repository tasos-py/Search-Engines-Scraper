from bs4 import BeautifulSoup
from time import sleep
from random import uniform as random_uniform
from . import utilities as utl
import config as cfg


class Search(object):
    '''The base class.'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        self._name = None
        self._http = utl.Http(timeout, proxy) 
        self._delay = (1, 4)
        self._domains = []
        self._query = ''

        self.results = Results()
        '''The search results.'''
        self.blacklist = cfg.blacklist
        '''Domains in this list are ignored.'''
        self.unique_domains = False
        '''Does not collect douplicate domains.'''
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        raise NotImplementedError()
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        raise NotImplementedError()
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data.'''
        raise NotImplementedError()
    
    def _get_url(self, tag, item='href'):
        '''Returns the URL of search results items.'''
        selector = self._selectors('url')
        url = self._get_tag_item(tag.select_one(selector), item)
        return utl.unquote_url(url)
    
    def _get_title(self, tag, item='text'):
        '''Returns the title of search results items.'''
        selector = self._selectors('title')
        return self._get_tag_item(tag.select_one(selector), item)
    
    def _get_text(self, tag, item='text'):
        '''Returns the text of search results items.'''
        selector = self._selectors('text')
        return self._get_tag_item(tag.select_one(selector), item)
    
    def _get_page(self, page, data=None, ref=None):
        '''Gets pagination links.'''
        if data:
            return self._http.post(page, data, ref)
        return self._http.get(page, ref)
    
    def _filter_query(self, query):
        '''Splits query to filter, query.'''
        filters = (
            u'inurl', u'intitle', u'intext', u'inhost', 
            u'url', u'title', u'text', u'host'
        )
        query = utl.decode_bytes(query)
        if query.split(u':')[0].lower() in filters:
            _filter, query = query.split(u':', 1) 
        else:
            _filter = u''
        return (query, _filter.strip().lower())
    
    def _get_tag_item(self, tag, item):
        '''Returns Tag attributes.'''
        if tag:
            return tag.text if item == 'text' else tag.get(item, u'')
        return u''
    
    def _items(self, link):
        '''Returns a dictionary of the link items.'''
        items = {
            'host': utl.domain(self._get_url(link)), 
            'link': self._get_url(link), 
            'title': self._get_title(link).strip(), 
            'text': self._get_text(link).strip()
        } 
        return items
    
    def _query_in(self, item):
        '''Checks if query is contained in the item.'''
        return self._query.lower() in item.lower()
    
    def _collect_results(self, tags):
        '''Collects links from search results page.''' 
        tags = tags.select(self._selectors('links'))
        links = [self._items(l) for l in tags]
        if 'url' in self._filter:
            links = [l for l in links if self._query_in(l['link'])]
        elif 'title' in self._filter:
            links = [l for l in links if self._query_in(l['title'])]
        elif 'text' in self._filter:
            links = [l for l in links if self._query_in(l['text'])]
        elif 'host' in self._filter:
            links = [l for l in links if self._query_in(utl.domain(l['link']))]
        return links

    def set_user_agent(self, ua_string):
        '''Sets the User-Agent string.'''
        self._http.client.headers['User-Agent'] = ua_string
    
    def search(self, query, pages=cfg.max_pages, unique=False): 
        '''
        Queries the search engine, goes through all pages and collects the results.
        
        :param query: str The search query
        :param pages: int Optional, the number of search results pages
        :param unique: bool Optional, collects unique domains only
        :returns Results
        '''
        self._query, self._filter = self._filter_query(query)
        _pages = [self._first_page()]
        utl.console('\rSearching {}'.format(self._name))

        while len(_pages) <= pages and _pages[-1]['url'] is not None:
            ref = _pages[-2]['url'] if len(_pages) > 1 else None
            try:
                request = self._get_page(_pages[-1]['url'], _pages[-1]['data'], ref)
                if request['http'] == 200:
                    tags = BeautifulSoup(request['html'], "html.parser")
                    items = self._collect_results(tags)

                    for item in items:
                        domain, url = item['host'], item['link']
                        if not utl.is_url(url):
                            continue
                        if (unique and domain in self._domains) or domain in self.blacklist: 
                            continue 
                        if item in self.results.results():
                            continue
                        self.results._results += [item]
                        self._domains += [domain]
                    
                    msg = '\rpage: {:<8} links: {}'.format(len(_pages), len(self.results))
                    utl.console(msg, end='')
                    _pages += [self._next_page(tags)]
                else:
                    msg = ('HTTP ' + str(request['http'])) if request['http'] else request['html']
                    utl.console(u'\rError: {:<20}'.format(msg))
                    break
                sleep(random_uniform(*self._delay))
            except KeyboardInterrupt:
                break
        utl.console('\r\t\t\t\t\r', end='')
        return self.results
    
    def report(self, output=None):
        '''
        Prints search results and creates report files.
        
        :param output: str Optional, the report format (html, csv).
        '''
        utl.console(' ')
        utl.print_results([self])
        file_name = u'_'.join(self._query.split())
        path = cfg.report_files_dir + file_name

        if 'html' in str(output).lower():
            utl.write_file(utl.html_results([self]), path + u'.html') 
        if 'csv' in str(output).lower():
            utl.write_file(utl.csv_results([self]), path + u'.csv') 


class Results:
    '''Holds the search results'''
    def __init__(self, items=None):
        self._results = items or []
    
    def links(self):
        '''Returns a list of results links'''
        return [row.get('link') for row in self._results]
    
    def titles(self):
        '''Returns a list of results titles'''
        return [row.get('title') for row in self._results]
    
    def text(self):
        '''Returns a list of results text'''
        return [row.get('text') for row in self._results]
    
    def hosts(self):
        '''Returns a list of results domains'''
        return [row.get('host') for row in self._results]
    
    def results(self):
        '''Returns all search results'''
        return self._results
    
    def __getitem__(self, index):
        return self._results[index]
    
    def __len__(self):
        return len(self._results)

    def __str__(self):
        return 'Results <{} items>'.format(len(self._results))



