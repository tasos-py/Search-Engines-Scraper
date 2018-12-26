from .engine import Search, Results
from . import config as cfg
from . import utilities as utl


class Google(Search):
    '''Searches google.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Google, self).__init__(proxy, timeout)
        self._name = 'Google' 
        self._start_page = 'https://www.google.com'
        self._delay = (2, 6)
	
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a[href]', 
            'title': 'a', 
            'text': 'span.st', 
            'links': 'div#search div#ires div.g', 
            'next': 'table#nav tr td[style="text-align:left"] a[href]'
        }
        return selectors[element]
    
    def _get_url(self, tag, item='href'):
        '''Returns the URL of search results item.'''
        selector = self._selectors('url')
        link = self._get_tag_item(tag.select_one(selector), item)
        url = utl.unquote_url(link.replace(u'/url?q=', u'').split(u'&sa=')[0])
        return utl.unquote_url(url)
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        page = u'{}/search?q={}&btnG=Search&gbv=1'.format(self._start_page, self.query)
        return {'num':1, 'url':page, 'data':None}
    
    def _next_page(self, tags, this_page):
        '''Returns the next page number, URL, post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = (self._start_page + next_page) if next_page else None
        return {'num':this_page + 1, 'url':url, 'data':None}


class Bing(Search):
    '''Searches bing.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Bing, self).__init__(proxy, timeout)
        self._start_page = 'https://www.bing.com'
        self._name = 'Bing' 

    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a[href]', 
            'title': 'a', 
            'text': 'p', 
            'links': 'ol#b_results > li.b_algo', 
            'next': 'div#b_content nav[role="navigation"] a.sb_pagN'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        page = u'{}/search?q={}'.format(self._start_page, self.query)
        return {'num':1, 'url':page, 'data':None}
    
    def _next_page(self, tags, this_page):
        '''Returns the next page number, URL, post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = (self._start_page + next_page) if next_page else None
        return {'num':this_page + 1, 'url':url, 'data':None}


class Yahoo(Search):
    '''Searches yahoo.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Yahoo, self).__init__(proxy, timeout)
        self._start_page = 'https://uk.search.yahoo.com'
        self._name = 'Yahoo'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'div.compTitle.options-toggle div span', 
            'title': 'h3.title', 
            'text': 'div.compText.aAbs p', 
            'links': 'div#main div#web li div.dd.algo.algo-sr.Sr', 
            'next': 'a.next'
        }
        return selectors[element]
    
    def _get_url(self, link, item='text'):
        selector = self._selectors('url')
        return u'http://' + self._get_tag_item(link.select_one(selector), item)
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        page = u'{}/search?p={}&ei=UTF-8&nojs=1'.format(self._start_page, self.query)
        return {'num':1, 'url':page, 'data':None}
    
    def _next_page(self, tags, this_page): 
        '''Returns the next page number, URL, post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        return {'num':this_page+1, 'url':next_page or None, 'data':None}


class Duckduckgo(Search):
    '''Searches duckduckgo.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Duckduckgo, self).__init__(proxy, timeout)
        self._start_page = 'https://duckduckgo.com/html/'
        self._name = 'Duckduckgo'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.result__snippet', 
            'title': 'h2.result__title a', 
            'text': 'a.result__snippet', 
            'links': 'div.results div.result.results_links.results_links_deep.web-result', 
            'next': ('div.nav-link form', 'input[value="Next"]')
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        data = {'q':self.query, 'b':'', 'kl':'us-en'} 
        return {'num':1, 'url':self._start_page, 'data':data}
    
    def _next_page(self, tags, this_page):
        '''Returns the next page number, URL, post data (if any)'''
        selector = self._selectors('next')
        next_page = [i for i in tags.select(selector[0]) if i.select(selector[1])]
        if next_page:
            data = {i['name']:i.get('value', '') for i in next_page[0].select('input[name]')}
            return {'num':this_page + 1, 'url':self._start_page, 'data':data}
        return {'num':this_page + 1, 'url':None, 'data':None}


class Startpage(Search):
    '''Searches startpage.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
        super(Startpage, self).__init__(proxy, timeout)
        self._start_page = 'https://www.startpage.com/do/asearch'
        self._name = 'Startpage'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'h3.search-item__title a', 
            'title': 'h3.search-item__title a', 
            'text': 'p.search-item__body', 
            'links': 'li.search-result.search-item', 
            'next': ('nav.pagination form[name=search-pagination]', 'button[name=startat]')
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        data = { 
            'query':self.query, 'cat':'web', 'cmd':'process_search', 
            'language':'english_uk', 'engine0':'v1all', 
            'nj':'1', 't':'air', 'abp':'-1', 'submit1':'GO'
        }
        return {'num':1, 'url':self._start_page, 'data':data}
    
    def _next_page(self, tags, this_page):
        '''Returns the next page number, URL, post data (if any)'''
        selector = self._selectors('next')
        next_page = tags.select_one(selector[0])
        if next_page:
            next_button = tags.select(selector[1])[1]['value'] ## test it ##
            if next_button != '-1':
                data = {i['name']:i.get('value', '') for i in next_page.select('input[name]')}
                data['startat'] = next_button
                return {'num':this_page + 1, 'url':next_page.get('action'), 'data':data} 
        return {'num':this_page + 1, 'url':None, 'data':None} 


class Ask(Search):
    '''Searches ask.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Ask, self).__init__(proxy, timeout)
        self._start_page = 'https://uk.ask.com'
        self._name = 'Ask'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.PartialSearchResults-item-title-link.result-link', 
            'title': 'a.PartialSearchResults-item-title-link.result-link', 
            'text': 'p.PartialSearchResults-item-abstract', 
            'links': 'div.PartialSearchResults-body div.PartialSearchResults-item', 
            'next': 'ul.PartialWebPagination a[href]'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        page = u'{}/web?q={}&qo=homepageSearchBox'.format(self._start_page, self.query)
        return {'num':1, 'url':page, 'data':None}
    
    def _next_page(self, tags, this_page):
        '''Returns the next page number, URL, post data (if any)'''
        next_page = tags.select(self._selectors('next'))
        url = (self._start_page + next_page[-1]['href']) if next_page else None
        return {'num':this_page + 1, 'url':url, 'data':None}


class Dogpile(Search):
    '''Seaches dogpile.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Dogpile, self).__init__(proxy, timeout)
        self._start_page = 'http://results.dogpile.com'
        self._name = 'Dogpile'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.web-google__result-url', 
            'title': 'a.web-google__result-title', 
            'text': 'span', 
            'links': 'div.web-google__result', 
            'next': 'a.pagination__num--next'
        }
        return selectors[element]
    
    def _get_url(self, link, item='text'):
        return self._get_tag_item(link.select_one(self._selectors('url')), 'href')
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        page = u'{}/serp?q={}'.format(self._start_page, self.query)
        return {'num':1, 'url':page, 'data':None}
    
    def _next_page(self, tags, this_page):
        '''Returns the next page number, URL, post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = (self._start_page + next_page) if next_page else None
        return {'num':this_page+1, 'url':url, 'data':None} 


class Searx(Search):
    '''Searches searx.me'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Searx, self).__init__(proxy, timeout)
        self._start_page = 'https://searx.me'
        self._name = 'Searx'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'h4.result_header a[href]', 
            'title': 'h4.result_header a', 
            'text': 'p.result-content', 
            'links': 'div#main_results div.result.result-default', 
            'next': 'div#pagination div.pull-right form'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        data = {
            'q':self.query, 
            'category_general':'on', 'time_range':'', 'language':'all'
        }
        return {'num':1, 'url':self._start_page, 'data':data}
    
    def _next_page(self, tags, this_page):
        '''Returns the next page number, URL, post data (if any)'''
        next_page = tags.select_one(self._selectors('next'))
        if next_page:
            data = {i['name']:i.get('value', '') for i in next_page.select('input')}
            url = self._start_page + next_page['action']
            return {'num':this_page + 1, 'url':url, 'data':data}
        return {'num':this_page + 1, 'url':None, 'data':None}


class Unbubble(Search):
    '''Seaches unbubble.eu'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Unbubble, self).__init__(proxy, timeout)
        self._start_page = 'https://www.unbubble.eu'
        self._name = 'Unbubble'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'div.link a[href]', 
            'title': 'h3.title', 
            'text': 'div.snippet', 
            'links': 'ol.result-list div.text-col', 
            'next': 'div.page-switcher a[rel=next]'
        }
        return selectors[element]
    
    def _get_url(self, link, item='href'):
        link = self._get_tag_item(link.select_one(self._selectors('url')), item)
        return utl.unquote_url(link.split(u'/?u=')[1])

    def _first_page(self):
        '''Returns the initial page and query.'''
        page = u'{}/?q={}&focus=web&rc=100&rp=1'.format(self._start_page, self.query)
        return {'num':1, 'url':page, 'data':None}
    
    def _next_page(self, tags, this_page):
        '''Returns the next page number, URL, post data (if any)'''
        next_page = self._get_tag_item(tags.select_one(self._selectors('next')), 'href')
        url = (self._start_page + next_page) if next_page else None
        return {'num':this_page + 1, 'url':url, 'data':None} 


class Torch(Search):
    '''Uses torch search engine. Requires tor proxy.'''
    def __init__(self, proxy=cfg.tor, timeout=cfg.timeout):
        super(Torch, self).__init__(proxy, timeout)
        self._start_page = 'http://xmh57jrzrnw6insl.onion/4a1f6b371c/search.cgi'
        self._name = 'Torch'
        if not proxy:
            print('Warning: Torch requires tor proxy!')
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'dt a[href]', 
            'title': 'dt a[href]', 
            'text': 'dd table tr td small', 
            'links': 'body dl', 
            'next': ('table tr td a[href]', 'Next >>')
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        page = u'{}?q={}&cmd=Search!&ps=50'.format(self._start_page, self.query)
        return {'num':1, 'url':page, 'data':None}
    
    def _next_page(self, tags, this_page):
        '''Returns the next page number, URL, post data (if any)'''
        _next = self._selectors('next')
        next_page = [i['href'] for i in tags.select(_next[0]) if i.text == _next[1]]
        url = (self._start_page + next_page[0]) if next_page else None
        return {'num':this_page + 1, 'url':url, 'data':None}


search_engines = { 
    'google': Google, 
    'bing': Bing, 
    'yahoo': Yahoo, 
    'duckduckgo': Duckduckgo, 
    'startpage': Startpage, 
    'dogpile': Dogpile, 
    'ask': Ask, 
    'searx': Searx, 
    'unbubble': Unbubble, 
    'torch': Torch 
}


class Multi(object):
    '''Uses multiple search engines.'''
    def __init__(self, engines, proxy=cfg.proxy, timeout=cfg.timeout):
        self.engines = [
            e(proxy, timeout) 
            for e in search_engines.values() 
            if e.__name__.lower() in engines
        ]
        self.results = Results()

    def search(self, query, pages=cfg.max_pages, unique=False): 
        '''Searches all engines.'''
        for engine in self.engines:
            self.results._results += engine.search(query, pages, unique)._results
        self.query = self.engines[0].query
        return self.results
    
    def report(self, output=''):
        '''
        Prints search results and creates report files.

        :param output: str Optional, the report format (html, csv).
        '''
        print(' ')
        utl.results_print(self.engines)
        file_name = ''.join(i if i.isalnum() else u'_' for i in self.query)
		
        if 'html' in output.lower():
            path = cfg.report_files_dir + file_name + '.html'
            utl.write_file(utl.results_html(self.engines), path) 
        if 'csv' in output.lower():
            path = cfg.report_files_dir + file_name + '.csv'
            utl.write_file(utl.results_csv(self.engines), path) 


class All(Multi):
    '''Uses all search engines.'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(All, self).__init__(
            list(search_engines), proxy, timeout
        )



