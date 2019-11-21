from .engine import Search, Results, BeautifulSoup
from . import utilities as utl
from .. import config as cfg


class Google(Search):
    '''Searches google.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Google, self).__init__(proxy, timeout)
        self._name = 'Google' 
        self._base_url = 'https://www.google.com'
        self._delay = (2, 6)
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a[href]', 
            'title': 'a', 
            'text': 'span.st', 
            'links': 'div#search div.g', 
            'next': 'table#nav td.b.navend a#pnnext'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url = u'{}/search?q={}'.format(self._base_url, self._query)
        return (url, None)
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = (self._base_url + next_page) if next_page else None
        return (url, None)

    def _get_url(self, tag, item='href'):
        '''Returns the URL of search results item.'''
        selector = self._selectors('url')
        link = self._get_tag_item(tag.select_one(selector), item)
        url = utl.unquote_url(link.replace(u'/url?q=', u'').split(u'&sa=')[0])
        return utl.unquote_url(url)


class Bing(Search):
    '''Searches bing.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Bing, self).__init__(proxy, timeout)
        self._base_url = 'https://www.bing.com'
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
        url = u'{}/search?q={}'.format(self._base_url, self._query)
        return (url, None)
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = (self._base_url + next_page) if next_page else None
        return (url, None)


class Yahoo(Search):
    '''Searches yahoo.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Yahoo, self).__init__(proxy, timeout)
        self._base_url = 'https://uk.search.yahoo.com'
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
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url = u'{}/search?p={}&ei=UTF-8&nojs=1'.format(self._base_url, self._query)
        return (url, None)
    
    def _next_page(self, tags): 
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        return (next_page or None, None)

    def _get_url(self, link, item='href'):
        selector = self._selectors('url')
        url = self._get_tag_item(link.select_one(selector), 'text')
        return utl.unquote_url(u'http://{}'.format(url))


class Duckduckgo(Search):
    '''Searches duckduckgo.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Duckduckgo, self).__init__(proxy, timeout)
        self._base_url = 'https://duckduckgo.com/html/'
        self._name = 'Duckduckgo'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.result__snippet', 
            'title': 'h2.result__title a', 
            'text': 'a.result__snippet', 
            'links': 'div.results div.result.results_links.results_links_deep.web-result', 
            'next': 'div.nav-link form input[name]'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        data = {'q':self._query, 'b':'', 'kl':'us-en'} 
        return self._base_url, data
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        inputs = tags.select(self._selectors('next'))
        url, data = None, None
        if inputs:
            data = {i['name']:i.get('value', '') for i in inputs}
            url = self._base_url
        return url, data


class Startpage(Search):
    '''Searches startpage.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
        super(Startpage, self).__init__(proxy, timeout)
        self._base_url = 'https://www.startpage.com'
        self._name = 'Startpage'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.w-gl__result-url', 
            'title': 'a.w-gl__result-title h3', 
            'text': 'p.w-gl__description', 
            'links': 'section.w-gl.w-gl--default div.w-gl__result', 
            'next': {'form':'form.pagination__form', 'text':'Next'} 
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        data = { 
            'query':self._query, 'cat':'web', 'cmd':'process_search', 
            'language':'english_uk', 'engine0':'v1all', 
            'pg':0, 'abp':-1
        }
        url = self._base_url + '/sp/search'
        return url, data
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        forms = [
            form for form in tags.select(selector['form']) 
            if form.get_text(strip=True) == selector['text']
        ]
        url, data = None, None
        if forms:
            url = self._base_url + forms[0]['action']
            data = {
                i['name']:i.get('value', '') 
                for i in forms[0].select('input')
            }
        return url, data


class Ask(Search):
    '''Searches ask.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Ask, self).__init__(proxy, timeout)
        self._base_url = 'https://uk.ask.com'
        self._name = 'Ask'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a.PartialSearchResults-item-title-link.result-link', 
            'title': 'a.PartialSearchResults-item-title-link.result-link', 
            'text': 'p.PartialSearchResults-item-abstract', 
            'links': 'div.PartialSearchResults-body div.PartialSearchResults-item', 
            'next': 'li.PartialWebPagination-next a[href]'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        page = u'{}/web?o=0&l=dir&qo=serpSearchTopBox&q={}'
        url = page.format(self._base_url, self._query)
        return url, None
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        next_page = tags.select_one(self._selectors('next'))
        url = None
        if next_page:
            url = self._base_url + next_page['href']
        return url, None


class Dogpile(Search):
    '''Seaches dogpile.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Dogpile, self).__init__(proxy, timeout)
        self._base_url = 'https://www.dogpile.com'
        self._name = 'Dogpile'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'a[class$=title]', 
            'title': 'a[class$=title]', 
            'text': {'selector':'span', 'index':-1}, 
            'links': 'div[class^=web-] div[class$=__result]', 
            'next': 'a.pagination__num--next'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url = u'{}/serp?q={}'.format(self._base_url, self._query)
        return url, None
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = (self._base_url + next_page) if next_page else None
        return url, None

    def _get_url(self, link, item='text'):
        selector = self._selectors('url')
        url = self._get_tag_item(link.select_one(selector), 'href')
        return utl.unquote_url(url)

    def _get_text(self, tag, item='text'):
        '''Returns the text of search results items.'''
        selector = self._selectors('text')
        tag = tag.select(selector['selector'])[selector['index']]
        return self._get_tag_item(tag, item)


class Searx(Search):
    '''Searches searx.me'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Searx, self).__init__(proxy, timeout)
        self._base_url = 'https://searx.me'
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
            'q':self._query, 
            'category_general':'on', 'time_range':'', 'language':'all'
        }
        return self._base_url, data
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        next_page = tags.select_one(self._selectors('next'))
        url, data = None, None
        if next_page:
            data = {i['name']:i.get('value', '') for i in next_page.select('input')}
            url = self._base_url + next_page['action']
        return url, data


class Aol(Search):
    '''Seaches Aol.eu'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Aol, self).__init__(proxy, timeout)
        self._base_url = 'https://search.aol.com'
        self._name = 'Aol'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'div.compTitle > div > span', 
            'title': 'div.compTitle h3.title', 
            'text': 'div.compText', 
            'links': 'ol.searchCenterMiddle li', 
            'next': 'div.compPagination a.next'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        s = u'{}/aol/search?q={}'
        return (s.format(self._base_url, self._query), None)
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        css = self._selectors('next')
        return (self._get_tag_item(tags.select_one(css), 'href'), None)

    def _get_url(self, link, item='text'):
        url = self._get_tag_item(link.select_one(self._selectors('url')), item)
        return 'http://' + utl.unquote_url(url)


class Torch(Search):
    '''Uses torch search engine. Requires TOR proxy.'''
    def __init__(self, proxy=cfg.tor, timeout=cfg.timeout):
        super(Torch, self).__init__(proxy, timeout)
        self._base_url = 'http://xmh57jrzrnw6insl.onion/4a1f6b371c/search.cgi'
        self._name = 'Torch'
        if not proxy:
            utl.console('Torch requires TOR proxy!', level=utl.Level.warning)
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'dt a[href]', 
            'title': 'dt a[href]', 
            'text': 'dd table tr td small', 
            'links': 'body dl', 
            'next': {'selector':'table tr td a[href]', 'text':'Next >>'}
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        url = u'{}?q={}&cmd=Search!&ps=50'.format(self._base_url, self._query)
        return url, None
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = [
            i['href'] for i in tags.select(selector['selector']) 
            if i.text == selector['text']
        ]
        url = (self._base_url + next_page[0]) if next_page else None
        return url, None


engines_dict = { 
    'google': Google, 
    'bing': Bing, 
    'yahoo': Yahoo, 
    'duckduckgo': Duckduckgo, 
    'startpage': Startpage, 
    'dogpile': Dogpile, 
    'ask': Ask, 
    'searx': Searx, 
    'aol': Aol, 
    'torch': Torch, 
}


class Multi(object):
    '''Uses multiple search engines.'''
    def __init__(self, engines, proxy=cfg.proxy, timeout=cfg.timeout):
        self._engines = [
            e(proxy, timeout) 
            for e in engines_dict.values() 
            if e.__name__.lower() in engines
        ]
        self.results = Results()
        self.unique_urls = False
        self.unique_domains = False
        self._filter = None

    def set_search_operator(self, operator):
        '''Filters search results based on the operator.'''
        self._filter = operator
    
    def search(self, query, pages=cfg.search_pages): 
        '''Searches all engines and collects teh results.'''
        for engine in self._engines:
            engine.unique_urls = self.unique_urls
            engine.unique_domains = self.unique_domains
            if self._filter:
                engine.set_search_operator(self._filter)

            for item in engine.search(query, pages):
                if self.unique_urls and item['link'] in self.results.links():
                    continue
                if self.unique_domains and item['host'] in self.results.hosts():
                    continue
                self.results._results.append(item)
        self._query = self._engines[0]._query
        return self.results
    
    def report(self, output=None, path=None):
        '''Prints search results and/or creates report files.'''
        utl.console(' ')
        utl.print_results(self._engines)
        if not self.results._results:
            return
        if not path:
            path = u'_'.join(self._query.split())
            path = cfg.os_path.join(cfg.report_files_dir, path)

        if 'html' in str(output).lower():
            utl.write_file(utl.html_results(self._engines), path + u'.html') 
        if 'csv' in str(output).lower():
            utl.write_file(utl.csv_results(self._engines), path + u'.csv')
        if 'json' in str(output).lower():
            utl.write_file(utl.json_results(self._engines), path + u'.json')


class All(Multi):
    '''Uses all search engines.'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(All, self).__init__(
            list(engines_dict), proxy, timeout
        )

