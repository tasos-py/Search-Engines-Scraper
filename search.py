import argparse
from core.engines import *
from core import config


if __name__ == '__main__': 
	ap = argparse.ArgumentParser()	
	ap.add_argument('-q', help='query', required=True)
	ap.add_argument('-e', help='search engine - '+', '.join(search_engines.keys()), default='google')
	ap.add_argument('-r', help='report [print, html, csv]', default='print')
	ap.add_argument('-l', help='max links', default=config.max_links, type=int)
	ap.add_argument('-p', help='max pages', default=config.max_pages, type=int)
	ap.add_argument('-u', help='unique results', action='store_true')
	ap.add_argument('-proxy', help='use proxy (scheme://ip:port)', default=config.proxy)
	ap.add_argument('-tor', help='use tor proxy', action='store_true')
	args = ap.parse_args()
	
	query = args.q
	engines = [e.lower().strip() for e in args.e.split(',') if e.strip()]
	proxy = args.proxy or (config.tor if args.tor else None)
	timeout = config.timeout if not proxy else config.timeout + 10
	search_engines = dict(search_engines)
	search_engines['all'] = All
	
	if len(engines) == 1 and engines[0] in search_engines: 
		engine = engines[0]
		se = search_engines[engine](proxy, timeout)
		se.search(query, args.l, args.p, args.u)
		se.report(args.r)
	elif len(engines) > 1 and any(e in search_engines for e in engines):
		se = Multi(engines, proxy, timeout)
		se.search(query, args.l, args.p, args.u)
		se.report(args.r)
	else: 
		print('Choose a search engine: \n'+', '.join(search_engines.keys())) 


