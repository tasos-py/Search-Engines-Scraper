from __future__ import print_function
from bs4 import BeautifulSoup
from time import sleep
from random import uniform
from . import utilities as utl
from . import config as cfg


class Search(object): 
	'''Parent class.'''
	blacklist = cfg.blacklist
	
	def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
		self.http = utl.Http(timeout, proxy) 
		self.delay = (1, 4)
		self.max_pages = cfg.max_pages
		self.results = []
		self.domains = []
	
	def first_page(self): 
		'''Interface method'''
	
	def next_page(self, tags, curr_page): 
		'''Interface method'''
	
	def _get_tag_attr(self, tag, item): 
		'''Returns Tag attributes.'''
		if tag: 
			return tag.text if item == 'text' else tag.get(item, '')
		return ''
	
	def _get_page(self, page, data=None, ref=None): 
		'''Gets pagination links.'''
		return self.http.post(page, data, ref) if data else self.http.get(page, ref)
	
	def _get_url(self, link, item='href'): 
		'''Returns the URL of search results items.'''
		return self._get_tag_attr(link.select_one(self._url), item)
	
	def _get_title(self, link, item='text'): 
		'''Returns the title of search results items.'''
		return self._get_tag_attr(link.select_one(self._title), item)
	
	def _get_text(self, link, item='text'): 
		'''Returns the text of search results items.'''
		return self._get_tag_attr(link.select_one(self._text), item)
	
	def _filter(self, query): 
		'''Splits query to filter, query.'''
		filters = ('inurl', 'intitle', 'intext', 'url', 'title', 'text')
		if query.split(':')[0].lower() in filters: 
			filter, query = query.split(':', 1)
		else : 
			filter = ''
		return (query, filter)
	
	def _items(self, link): 
		'''Returns a dictionary of the link items.'''
		url = self._get_url(link)
		return {'domain':utl._domain(url), 'link':url, 'title':self._get_title(link), 'text':self._get_text(link)} 
	
	def _extract(self, tags): 
		'''Collects links from search results page.''' 
		links = tags.select(self._links)
		if 'url' in self.filter: 
			links = [self._items(l) for l in links if self.query.lower() in self._get_url(l).lower()]
		elif 'title' in self.filter: 
			links = [self._items(l) for l in links if self.query.lower() in self._get_title(l).lower()]
		elif 'text' in self.filter: 
			links = [self._items(l) for l in links if self.query.lower() in self._get_text(l).lower()]
		else: 
			links = [self._items(l) for l in links]
		return links
	
	def search(self, query, max_results=cfg.max_results, unique=False, output=False): 
		'''
		Queries the search engine, goes through all the pages and collects the results.
		
		:param query: str
		:param max_results: int, optional
		:param unique: bool, optional, collect unique domains only
		:param output: bool, optional, print progress
		'''
		self.query, self.filter = self._filter(query)
		pages = [self.first_page()] 
		if output: 
			print('Searching', self.engine, 'for', self.query)
		while len(self.results) < max_results: 
			ref = pages[-2]['url'] if len(pages) > 1 else None
			try: 
				request = self._get_page(pages[-1]['url'], pages[-1]['data'], ref)
				if request['http'] == 200: 
					tags = BeautifulSoup(request['html'], "html.parser")
					links = self._extract(tags)
					for item in links:
						domain, url = item['domain'], item['link']
						if not utl._is_url(url): 
							continue
						if (unique and domain in self.domains) or domain in self.blacklist: 
							continue 
						if item in self.results: 
							continue
						self.results += [item]
						self.domains += [domain]
					if output: 
						print('\rpage:{:<8} links:{}'.format(pages[-1]['num'], len(self.results)), end='')
					pages += [self.next_page(tags, pages[-1]['num'])] 
					if pages[-1]['url'] is None: 
						break
					if pages[-1]['num'] > self.max_pages: 
						break 
				else: 
					if output:
						print('\rHTTP: {:<20}'.format(request['http']), end='')
					break
				sleep(uniform(*self.delay))
			except KeyboardInterrupt: 
				break
			except Exception as ex: 
				print('\nError: '+str(ex))
				break
		if output:
			print(' ') 
	
	def report(self, rep='print'): 
		'''
		Prints search results, creates report files.
		:param rep: str
		'''
		print(' ') 
		if 'print' in rep.lower(): 
			self._print([self])
		if 'html' in rep.lower(): 
			utl._write(self._html([self]), cfg.html_file) 
		if 'csv' in rep.lower():
			utl._write(self._csv([self]), cfg.csv_file) 
	
	def _print(self, engines):
		'''Prints the results.'''
		for se in engines: 
			print('Search Engine: ' + se.engine) 
			for i,v in enumerate(se.results):
				v = (utl._encode(v['link']) if cfg.python_version == 2 else v['link'])
				print('{:<3}{}'.format(i+1, v)) 
			print(' ')
	
	def _html(self, engines): 
		'''Creates html report.'''
		html = utl.Html
		tables = ''
		for se in engines: 
			rows = ''
			for i,v in enumerate(se.results):
				data = ''
				if 'title' in se.filter:
					data += html.data.format(v['title'])
				elif 'text' in se.filter:
					data += html.data.format(v['text'])
				rows += html.row.format(number=i+1, link=v['link'], data=data)
			tables += html.table.format(engine=se.engine, rows=rows) 
		return html.html.format(query=engines[0].query, table=tables)
	
	def _csv(self, engines):
		'''Creates csv report.'''
		_encode = utl._decode if cfg.python_version == 3 else utl._encode
		data = [['Query', 'Engine', 'Domain', 'URL', 'Title', 'Text']]
		for se in engines: 
			for item in se.results:
				items = [se.query, se.engine, item['domain'], item['link'], item['title'], item['text']]
				row = [_encode(i) for i in items]
				data.append(row)
		return data

