from bs4 import BeautifulSoup
from time import sleep
from random import uniform as random_uniform

from . import utilities as utl
from .. import config as cfg


class Search(object):
    '''The base class for all Search Engines.'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        self._name = None
        self._http = utl.Http(timeout, proxy) 
        self._delay = (1, 4)
        self._query = ''
        self._filter = ''

        self.results = Results()
        '''The search results.'''
        self.unique_urls = False
        '''Collects only unique URLs.'''
        self.unique_domains = False
        '''Collects only unique domains.'''

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
    
    def _filter_results(self, tags):
        '''Processes and filters the search results.''' 
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
    
    def _collect_results(self, items):
        '''Colects the search results items.''' 
        for item in items:
            if not utl.is_url(item['link']):
                continue
            if item in self.results._results:
                continue
            if self.unique_domains and item['link'] in self.results.links():
                continue
            if self.unique_domains and item['host'] in self.results.hosts():
                continue
            self.results._results += [item]

    def set_user_agent(self, ua_string):
        '''Sets the User-Agent string.'''
        self._http.client.headers['User-Agent'] = ua_string

    def set_search_operator(self, operator):
        '''
        Filters search results based on the operator. 
        Supported operators: 'url', 'title', 'text', 'host'

        :param operator: str The search operator
        '''
        operator = utl.decode_bytes(operator or '')
        operators = [u'url', u'title', u'text', u'host']

        if operator not in operators:
            msg = u'Ignoring unsupported operator: "{}"!'.format(operator)
            utl.console(msg, level=utl.Level.warning)
        else:
            self._filter = operator
    
    def search(self, query, pages=cfg.search_pages): 
        '''
        Queries the search engine, goes through the pages and collects the results.
        
        :param query: str The search query
        :param pages: int Optional, the number of pages to search
        :returns Results object
        '''
        utl.console('\rSearching {}'.format(self._name))
        self._query = utl.decode_bytes(query)
        ref, (url, data) = None, self._first_page()

        for page in range(1, pages + 1):
            try:
                resp = self._get_page(url, data, ref)
                if resp.http != 200:
                    msg = ('HTTP ' + str(resp.http)) if resp.http else resp.html
                    utl.console(u'\rError: {:<20}'.format(msg))
                    break
                tags = BeautifulSoup(resp.html, "html.parser")
                items = self._filter_results(tags)
                self._collect_results(items)
                
                msg = '\rpage: {:<8} links: {}'.format(page, len(self.results))
                utl.console(msg, end='')
                ref, (url, data) = url, self._next_page(tags)
                if not url:
                    break
                sleep(random_uniform(*self._delay))
            except KeyboardInterrupt:
                break
        utl.console('\r\t\t\t\t\t\t\r', end='')
        return self.results
    
    def report(self, output=None, path=None):
        '''
        Prints search results and/or creates report files.
        supported output format: html, csv, json.
        
        :param output: str Optional, the report format.
        :param path: str Optional, the file to save the report.
        '''
        utl.console(' ')
        utl.print_results([self])
        
        if not self.results._results:
            return
        if not path:
            path = u'_'.join(self._query.split())
            path = cfg.os_path.join(cfg.report_files_dir, path)

        if 'html' in (output or '').lower():
            utl.write_file(utl.html_results([self]), path + u'.html') 
        if 'csv' in (output or '').lower():
            utl.write_file(utl.csv_results([self]), path + u'.csv') 
        if 'json' in (output or '').lower():
            utl.write_file(utl.json_results([self]), path + u'.json') 


class Results:
    '''Holds the search results'''
    def __init__(self, items=None):
        self._results = items or []
    
    def links(self):
        '''Returns the links found in search results'''
        return [row.get('link') for row in self._results]
    
    def titles(self):
        '''Returns the titles found in search results'''
        return [row.get('title') for row in self._results]
    
    def text(self):
        '''Returns the text found in search results'''
        return [row.get('text') for row in self._results]
    
    def hosts(self):
        '''Returns the domains found in search results'''
        return [row.get('host') for row in self._results]
    
    def results(self):
        '''Returns all data found in search results'''
        return self._results
    
    def __getitem__(self, index):
        return self._results[index]
    
    def __len__(self):
        return len(self._results)

    def __str__(self):
        return 'Results <{} items>'.format(len(self._results))

