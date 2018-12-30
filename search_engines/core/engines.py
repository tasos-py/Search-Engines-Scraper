from .engine import Search, Results
from . import utilities as utl
import config as cfg


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
            'links': 'div#search div#ires div.g', 
            'next': 'table#nav td[style="text-align:left"] a[href]'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        page = u'{}/search?q={}&gbv=1'.format(self._base_url, self._query)
        return {'url':page, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = (self._base_url + next_page) if next_page else None
        return {'url':url, 'data':None}

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
        page = u'{}/search?q={}'.format(self._base_url, self._query)
        return {'url':page, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = (self._base_url + next_page) if next_page else None
        return {'url':url, 'data':None}


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
        page = u'{}/search?p={}&ei=UTF-8&nojs=1'.format(self._base_url, self._query)
        return {'url':page, 'data':None}
    
    def _next_page(self, tags): 
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        return {'url':next_page or None, 'data':None}

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
        return {'url':self._base_url, 'data':data}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        inputs = tags.select(self._selectors('next'))
        url, data = None, None
        if inputs:
            data = {i['name']:i.get('value', '') for i in inputs}
            url = self._base_url
        return {'url':url, 'data':data}


class Startpage(Search):
    '''Searches startpage.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
        super(Startpage, self).__init__(proxy, timeout)
        self._base_url = 'https://www.startpage.com/do/asearch'
        self._name = 'Startpage'
    
    def _selectors(self, element):
        '''Returns the appropriate CSS selector.'''
        selectors = {
            'url': 'h3.search-item__title a', 
            'title': 'h3.search-item__title a', 
            'text': 'p.search-item__body', 
            'links': 'li.search-result.search-item', 
            'next': {
                'form': 'nav.pagination form[name=search-pagination]', 
                'buttons': 'button[name=startat]'
            }
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        data = { 
            'query':self._query, 'cat':'web', 'cmd':'process_search', 
            'language':'english_uk', 'engine0':'v1all', 
            'nj':'1', 't':'air', 'abp':'-1', 'submit1':'GO'
        }
        return {'url':self._base_url, 'data':data}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        form = tags.select_one(selector['form'])
        buttons = tags.select(selector['buttons'])
        url, data = None, None

        if form and len(buttons) == 2 and buttons[1].get('value') != '-1':
            data = {i['name']:i.get('value', '') for i in form.select('input[name]')}
            data['startat'] = buttons[1]['value']
            url = form.get('action')
        return {'url':url, 'data':data}


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
            'next': 'ul.PartialWebPagination a[href]'
        }
        return selectors[element]
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        page = u'{}/web?q={}&qo=homepageSearchBox'.format(self._base_url, self._query)
        return {'url':page, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        next_page = tags.select(self._selectors('next'))
        url = (self._base_url + next_page[-1]['href']) if next_page else None
        return {'url':url, 'data':None}


class Dogpile(Search):
    '''Seaches dogpile.com'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Dogpile, self).__init__(proxy, timeout)
        self._base_url = 'http://results.dogpile.com'
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
        page = u'{}/serp?q={}'.format(self._base_url, self._query)
        return {'url':page, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = self._get_tag_item(tags.select_one(selector), 'href')
        url = (self._base_url + next_page) if next_page else None
        return {'url':url, 'data':None} 

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
        return {'url':self._base_url, 'data':data}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        next_page = tags.select_one(self._selectors('next'))
        url, data = None, None
        if next_page:
            data = {i['name']:i.get('value', '') for i in next_page.select('input')}
            url = self._base_url + next_page['action']
        return {'url':url, 'data':data}


class Unbubble(Search):
    '''Seaches unbubble.eu'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(Unbubble, self).__init__(proxy, timeout)
        self._base_url = 'https://www.unbubble.eu'
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
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        page = u'{}/?q={}&focus=web&rc=100&rp=1'.format(self._base_url, self._query)
        return {'url':page, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        next_page = self._get_tag_item(tags.select_one(self._selectors('next')), 'href')
        url = (self._base_url + next_page) if next_page else None
        return {'url':url, 'data':None} 

    def _get_url(self, link, item='href'):
        link = self._get_tag_item(link.select_one(self._selectors('url')), item)
        return utl.unquote_url(link.split(u'/?u=')[1])


class Torch(Search):
    '''Uses torch search engine. Requires tor proxy.'''
    def __init__(self, proxy=cfg.tor, timeout=cfg.timeout):
        super(Torch, self).__init__(proxy, timeout)
        self._base_url = 'http://xmh57jrzrnw6insl.onion/4a1f6b371c/search.cgi'
        self._name = 'Torch'
        if not proxy:
            utl.console('Torch requires tor proxy!', level=utl.Level.warning)
    
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
        page = u'{}?q={}&cmd=Search!&ps=50'.format(self._base_url, self._query)
        return {'url':page, 'data':None}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        selector = self._selectors('next')
        next_page = [
            i['href'] for i in tags.select(selector['selector']) 
            if i.text == selector['text']
        ]
        url = (self._base_url + next_page[0]) if next_page else None
        return {'url':url, 'data':None}


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
        self._query = self.engines[0]._query
        return self.results
    
    def report(self, output=None):
        '''
        Prints search results and creates report files.

        :param output: str Optional, the report format (html, csv).
        '''
        utl.console(' ')
        utl.print_results(self.engines)
        file_name = u'_'.join(self._query.split())
        path = cfg.report_files_dir + file_name

        if 'html' in str(output).lower():
            utl.write_file(utl.html_results(self.engines), path + u'.html') 
        if 'csv' in str(output).lower():
            utl.write_file(utl.csv_results(self.engines), path + u'.csv')


class All(Multi):
    '''Uses all search engines.'''
    def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout):
        super(All, self).__init__(
            list(search_engines), proxy, timeout
        )



