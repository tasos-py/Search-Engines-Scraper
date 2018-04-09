from .engine import *
from . import config as cfg
from .utilities import unquote, _write


class Google(Search): 
	'''Searches google'''
	_url = 'a[href]'
	_title = 'a'
	_text = 'span.st'
	_links = 'div#search div#ires div.g'
	_next = 'table#nav tr td[style="text-align:left"] a[href]'
	
	def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
		super(Google, self).__init__(proxy, timeout)
		self.engine = 'google' 
		self.start_page = 'https://www.google.com'
		self.delay = (2, 8)
	
	def _get_url(self, link, item='href'): 
		'''Returns the URL of search results item.'''
		link = self._get_tag_attr(link.select_one(self._url), item)
		return unquote(link.replace('/url?q=', '').split('&sa=')[0])
	
	def _first_page(self): 
		'''Returns the initial page and query.'''
		page = self.start_page + '/search?q=' + self.query + '&btnG=Search&gbv=1'
		return {'num':1, 'url':page, 'data':None}
	
	def _next_page(self, tags, curr_page): 
		'''Returns the next page number, URL, post data (if any)'''
		nextp = self._get_tag_attr(tags.select_one(self._next), 'href')
		url = (self.start_page + nextp) if nextp else None
		return {'num':curr_page+1, 'url':url, 'data':None}


class Bing(Search):
	'''Searches bing'''
	_url = 'a[href]'
	_title = 'a'
	_text = 'p'
	_links = 'ol#b_results > li.b_algo'
	_next = 'div#b_content nav[role="navigation"] a.sb_pagN'
	
	def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
		super(Bing, self).__init__(proxy, timeout)
		self.engine = 'bing'  
		self.start_page = 'https://www.bing.com'
	
	def _first_page(self): 
		'''Returns the initial page and query.'''
		page = self.start_page + '/search?q=' + self.query + '&go=Search&qs=ds&form=QBRE'
		return {'num':1, 'url':page, 'data':None}
	
	def _next_page(self, tags, curr_page): 
		'''Returns the next page number, URL, post data (if any)'''
		nextp = self._get_tag_attr(tags.select_one(self._next), 'href')
		url = (self.start_page + nextp) if nextp else None
		return {'num':curr_page+1, 'url':url, 'data':None}


class Yahoo(Search):
	'''Searches yahoo'''
	_url = 'div.compTitle.options-toggle div span'
	_title = 'h3.title'
	_text = 'div.compText.aAbs p'
	_links = 'div#main div#web li div.dd.algo.algo-sr.Sr'
	_next = 'a.next'
	
	def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
		super(Yahoo, self).__init__(proxy, timeout)
		self.engine = 'yahoo'  
		self.start_page = 'https://uk.search.yahoo.com'
	
	def _get_url(self, link, item='text'): 
		return 'http://' + self._get_tag_attr(link.select_one(self._url), item)
	
	def _first_page(self): 
		'''Returns the initial page and query.'''
		page = self.start_page + '/search?p=' + self.query + '&ei=UTF-8&nojs=1'
		return {'num':1, 'url':page, 'data':None}
	
	def _next_page(self, tags, curr_page): 
		'''Returns the next page number, URL, post data (if any)'''
		nextp = self._get_tag_attr(tags.select_one(self._next), 'href')
		return {'num':curr_page+1, 'url':nextp or None, 'data':None}


class Duckduckgo(Search): 
	'''Searches duckduckgo'''
	_url = 'a.result__snippet'
	_title = 'h2.result__title a'
	_text = 'a.result__snippet'
	_links = 'div.results div.result.results_links.results_links_deep.web-result'
	_next = ('div.nav-link form', 'input[value="Next"]')
	
	def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
		super(Duckduckgo, self).__init__(proxy, timeout)
		self.engine = 'duckduckgo' 
		self.start_page = 'https://duckduckgo.com' + '/html/'
	
	def _first_page(self): 
		'''Returns the initial page and query.'''
		data = {'q':self.query, 'b':'', 'kl':'us-en'} 
		return {'num':1, 'url':self.start_page, 'data':data}
	
	def _next_page(self, tags, curr_page): 
		'''Returns the next page number, URL, post data (if any)'''
		nextp = [i for i in tags.select(self._next[0]) if i.select(self._next[1])]
		if nextp: 
			data = {i['name']:i.get('value', '') for i in nextp[0].select('input[name]')}
			return {'num':curr_page+1, 'url':self.start_page, 'data':data}
		return {'num':curr_page+1, 'url':None, 'data':None}


class Startpage(Search):
	'''Searches startpage'''
	_url = 'div h3 a'
	_title = 'div h3 a span'
	_text = 'p.desc.clk'
	_links = 'ol.web_regular_results li'
	_next = 'form[name="nextform"]'
	
	def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
		super(Startpage, self).__init__(proxy, timeout)
		self.engine = 'startpage'  
		self.start_page = 'https://www.startpage.com'
	
	def _first_page(self): 
		'''Returns the initial page and query.'''
		page = self.start_page + '/do/asearch'
		data = { 
			'query':self.query, 'cat':'web', 'cmd':'process_search', 'language':'english_uk', 
			'engine0':'v1all', 'nj':'1', 't':'air', 'abp':'-1', 'submit1':'GO'
		}
		return {'num':1, 'url':page, 'data':data}
	
	def _next_page(self, tags, curr_page): 
		'''Returns the next page number, URL, post data (if any)'''
		nextp = tags.find('form', {'name':'nextform', 'action':True})
		if nextp: 
			data = {i['name']:i.get('value', '') for i in nextp.select('input[name]')}
			return {'num':curr_page+1, 'url':nextp.get('action'), 'data':data} 
		return {'num':curr_page+1, 'url':None, 'data':None}


class Ask(Search):
	'''Searches ask.'''
	_url = 'a.PartialSearchResults-item-title-link.result-link'
	_title = 'a.PartialSearchResults-item-title-link.result-link'
	_text = 'p.PartialSearchResults-item-abstract'
	_links = 'div.PartialSearchResults-body div.PartialSearchResults-item'
	_next = 'ul.PartialWebPagination a[href]'
	
	def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
		super(Ask, self).__init__(proxy, timeout)
		self.engine = 'ask'  
		self.start_page = 'https://uk.ask.com'
	
	def _first_page(self): 
		'''Returns the initial page and query.'''
		page = self.start_page + '/web?q=' + self.query + '&qo=homepageSearchBox'
		return {'num':1, 'url':page, 'data':None}
	
	def _next_page(self, tags, curr_page): 
		'''Returns the next page number, URL, post data (if any)'''
		nextp = tags.select(self._next)
		url = (self.start_page + nextp[-1]['href']) if nextp else None
		return {'num':curr_page+1, 'url':url, 'data':None}


class Dogpile(Search):
	'''Seaches dogpile.'''
	_url = 'div.resultDisplayUrlPane a'
	_title = 'div.resultTitlePane a'
	_text = 'div.resultDescription'
	_links = 'div#webResults div.searchResult.webResult'
	_next = 'div#resultsPaginationBottom li.paginationNext a[href]'
	
	def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
		super(Dogpile, self).__init__(proxy, timeout)
		self.engine = 'dogpile'  
		self.start_page = 'http://www.dogpile.com'
	
	def _get_url(self, link, item='text'): 
		return 'http://' + self._get_tag_attr(link.select_one(self._url), item)
	
	def _first_page(self): 
		'''Returns the initial page and query.'''
		page = self.start_page + '/search/web?q=' + self.query 
		return {'num':1, 'url':page, 'data':None}
	
	def _next_page(self, tags, curr_page): 
		'''Returns the next page number, URL, post data (if any)'''
		nextp = self._get_tag_attr(tags.select_one(self._next), 'href')
		url = (self.start_page + nextp) if nextp else None
		return {'num':curr_page+1, 'url':url, 'data':None} 


class Searx(Search):
	'''Uses searx.me search engine.'''
	_url = 'h4.result_header a[href]'
	_title = 'h4.result_header a'
	_text = 'p.result-content'
	_links = 'div#main_results div.result.result-default'
	_next = 'div#pagination div.pull-right form'
	
	def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
		super(Searx, self).__init__(proxy, timeout)
		self.engine = 'searx'  
		self.start_page = 'https://searx.me'
	
	def _first_page(self): 
		'''Returns the initial page and query.'''
		data = {'q':self.query, 'category_general':'on', 'time_range':'', 'language':'all'}
		return {'num':1, 'url':self.start_page+'/', 'data':data}
	
	def _next_page(self, tags, curr_page): 
		'''Returns the next page number, URL, post data (if any)'''
		nextp = tags.select_one(self._next)
		if nextp: 
			data = {i['name']:i.get('value', '') for i in nextp.select('input[value]')}
			return {'num':curr_page+1, 'url':self.start_page+nextp['action'], 'data':data}
		return {'num':curr_page+1, 'url':None, 'data':None}


class Torch(Search):
	'''Uses torch search engine. Requires tor proxy.'''
	_url = 'dt a[href]'
	_title = 'dt a[href]'
	_text = 'dd table tr td small'
	_links = 'body dl'
	_next = ('table tr td a[href]', 'Next >>')
	
	def __init__(self, proxy=cfg.tor, timeout=cfg.timeout): 
		super(Torch, self).__init__(proxy, timeout)
		self.engine = 'torch'  
		self.start_page = 'http://xmh57jrzrnw6insl.onion' + '/4a1f6b371c/search.cgi'
		if not proxy: 
			print('Warning: Torch requires tor proxy!')
	
	def _first_page(self): 
		'''Returns the initial page and query.'''
		page = self.start_page + '?q=' + self.query + '&cmd=Search!' 
		return {'num':1, 'url':page, 'data':None}
	
	def _next_page(self, tags, curr_page): 
		'''Returns the next page number, URL, post data (if any)'''
		nextp = [i['href'] for i in tags.select(self._next[0]) if i.text == self._next[1]]
		url = (self.start_page + nextp[0]) if nextp else None
		return {'num':curr_page+1, 'url':url, 'data':None}


search_engines = { 
	'google': Google, 
	'bing': Bing, 
	'yahoo': Yahoo, 
	'duckduckgo': Duckduckgo, 
	'startpage': Startpage, 
	'dogpile': Dogpile, 
	'ask': Ask, 
	'searx': Searx, 
	'torch': Torch 
	}


class All(object): 
	'''Uses all search engines.'''
	def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
		self.engines = [se(proxy, timeout) for se in search_engines.values()]
		self.results = Results()
	
	def search(self, query, max_links=cfg.max_links, max_pages=cfg.max_pages, unique=False): 
		'''Searches all engines.'''
		for se in self.engines : 
			se.search(query, max_links, max_pages, unique)
			self.results.items += se.results.items
		self.query = self.engines[0].query
		return self.results
	
	def report(self, rep='print'): 
		'''Prints the results, creates report files.'''
		print(' ') 
		Search._print(self.engines)
		if 'html' in rep.lower(): 
			path = cfg.files_dir + ''.join(i if i.isalnum() else '_' for i in self.query) + '.html'
			_write(Search._html(self.engines), path) 
		if 'csv' in rep.lower():
			path = cfg.files_dir + ''.join(i if i.isalnum() else '_' for i in self.query) + '.csv'
			_write(Search._csv(self.engines), path) 


class Multi(All): 
	'''Uses multiple search engines.'''
	def __init__(self, engines, proxy=cfg.proxy, timeout=cfg.timeout): 
		self.engines = [
			e(proxy, timeout) 
			for e in search_engines.values() 
			if e.__name__.lower() in engines
		]
		self.results = Results()


