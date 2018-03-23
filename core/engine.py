from __future__ import print_function
from bs4 import BeautifulSoup
from time import sleep
from random import uniform
from . import utilities as utl
from . import config as cfg


class Search(object): 
	'''Parent class.'''
	blacklist = cfg.blacklist
	_domains = []
	
	def __init__(self, proxy=cfg.proxy, timeout=cfg.timeout): 
		self.http = utl.Http(timeout, proxy) 
		self.delay = (1, 4)
		self.results = Results()
	
	def _get_tag_attr(self, tag, item): 
		'''Returns Tag attributes.'''
		if tag: 
			return tag.text if item == 'text' else tag.get(item, '')
		return ''
	
	def _get_page(self, page, data=None, ref=None): 
		'''Gets pagination links.'''
		if data:
			return self.http.post(page, data, ref)
		return self.http.get(page, ref)
	
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
		filters = ('inurl', 'intitle', 'intext', 'url', 'title', 'text', 'host')
		if query.split(':')[0].lower() in filters:
			filter, query = query.split(':', 1) 
		else: 
			filter = ''
		return (query, filter.lower())
	
	def _items(self, link): 
		'''Returns a dictionary of the link items.'''
		items = {
			'host':utl._domain(self._get_url(link)), 'link':self._get_url(link), 
			'title':self._get_title(link), 'text':self._get_text(link)
			} 
		return items
	
	def _query_in(self, item):
		'''Checks if query is contained in the item.'''
		return self.query.lower() in item.lower()
	
	def _extract(self, tags): 
		'''Collects links from search results page.''' 
		links = tags.select(self._links)
		if 'url' in self.filter: 
			links = [self._items(l) for l in links if self._query_in(self._get_url(l))]
		elif 'title' in self.filter: 
			links = [self._items(l) for l in links if self._query_in(self._get_title(l))]
		elif 'text' in self.filter: 
			links = [self._items(l) for l in links if self._query_in(self._get_text(l))]
		elif 'host' in self.filter: 
			links = [self._items(l) for l in links if self._query_in(utl._domain(self._get_url(l)))]
		else: 
			links = [self._items(l) for l in links]
		return links
	
	def _first_page(self): 
		'''Returns the initial page and query.'''
		pass
	
	def _next_page(self, tags, curr_page): 
		'''Returns the next page number, URL and post data'''
		pass
	
	def search(self, query, max_links=cfg.max_links, max_pages=cfg.max_pages, unique=False): 
		'''
		Queries the search engine, goes through all the pages and collects the results.
		
		:param query: str
		:param max_links: int, optional
		:param unique: bool, optional, collect unique domains only
		:returns Results
		'''
		self.query, self.filter = self._filter(query)
		pages = [self._first_page()] 
		print('Searching', self.engine, 'for', self.query)
		while len(self.results.items) < max_links and pages[-1]['num'] <= max_pages: 
			ref = pages[-2]['url'] if len(pages) > 1 else None
			try: 
				request = self._get_page(pages[-1]['url'], pages[-1]['data'], ref)
				if request['http'] == 200: 
					tags = BeautifulSoup(request['html'], "html.parser")
					links = self._extract(tags)
					for item in links:
						domain, url = item['host'], item['link']
						if not utl._is_url(url): 
							continue
						if (unique and domain in self._domains) or domain in self.blacklist: 
							continue 
						if len(self.results.items) >= max_links:
							continue
						if item in self.results.items: 
							continue
						self.results.items += [item]
						self._domains += [domain]
					print('\rpage:{:<8} links:{}'.format(pages[-1]['num'], len(self.results.items)), end='')
					pages += [self._next_page(tags, pages[-1]['num'])] 
					if pages[-1]['url'] is None: 
						break
				else: 
					error = ('HTTP ' + str(request['http'])) if request['http'] else request['html']
					print('\rError: {:<20}'.format(error), end='')
					break
				sleep(uniform(*self.delay))
			except KeyboardInterrupt: 
				break
			except Exception as e: 
				print('\nError: ' + str(e))
				break
		print(' ') 
		return self.results
	
	def report(self, rep='print'): 
		'''
		Prints search results, creates report files.
		
		:param rep: str, optional
		'''
		print(' ') 
		self._print([self])
		if 'html' in rep.lower(): 
			path = cfg.files_dir + ''.join(i if i.isalnum() else '_' for i in self.query) + '.html'
			utl._write(self._html([self]), cfg.html_file) 
		if 'csv' in rep.lower():
			path = cfg.files_dir + ''.join(i if i.isalnum() else '_' for i in self.query) + '.csv'
			utl._write(self._csv([self]), path) 
	
	@staticmethod
	def _print(engines):
		'''Prints the results.'''
		for se in engines: 
			print('Search Engine: ' + se.engine) 
			for i,v in enumerate(se.results.items):
				v = utl._encode(v['link']) if cfg.python_version == 2 else v['link']
				print('{:<3}{}'.format(i+1, v)) 
			print(' ')
	
	@staticmethod
	def _html(engines): 
		'''Creates html report.'''
		html = utl.Html
		tables = ''
		for se in engines: 
			rows = ''
			for i,v in enumerate(se.results.items):
				data = ''
				if 'title' in se.filter:
					data += html.data.format(v['title'])
				elif 'text' in se.filter:
					data += html.data.format(v['text'])
				rows += html.row.format(number=i+1, link=v['link'], data=data)
			tables += html.table.format(engine=se.engine, rows=rows) 
		return html.html.format(query=engines[0].query, table=tables)
	
	@staticmethod
	def _csv(engines):
		'''Creates csv report.'''
		_encode = utl._decode if cfg.python_version == 3 else utl._encode
		data = [['Query', 'Engine', 'Domain', 'URL', 'Title', 'Text']]
		for se in engines: 
			for i in se.results.items:
				row = [se.query, se.engine, i['host'], i['link'], i['title'], i['text']]
				row = [_encode(i) for i in row]
				data.append(row)
		return data


class Results:
	'''Holds the search results'''
	def __init__(self, items=None):
		self.items = items or []
	
	def links(self):
		'''Returns a list of results links'''
		return [row.get('link') for row in self.items]
	
	def titles(self):
		'''Returns a list of results titles'''
		return [row.get('title') for row in self.items]
	
	def text(self):
		'''Returns a list of results text'''
		return [row.get('text') for row in self.items]
	
	def hosts(self):
		'''Returns a list of results domains'''
		return [row.get('host') for row in self.items]
	
	def all(self):
		'''Returns all the items'''
		return self.items
	
	def __str__(self):
		return self.items.__str__()


