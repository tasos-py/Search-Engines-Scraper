import argparse
from core.engines import *
from core import config


if __name__ == '__main__': 
	ap = argparse.ArgumentParser()	
	ap.add_argument('-q', help='query', required=True)
	ap.add_argument('-e', help='search engine ' + str(search_engines.keys()), default='google')
	ap.add_argument('-p', help='use proxy (type://ip:port)', default=config.proxy)
	ap.add_argument('-m', help='max results', default=config.max_results, type=int)
	ap.add_argument('-u', help='unique results', action='store_true')
	ap.add_argument('-r', help='create report file [html, csv]', default='print')
	ap.add_argument('-tor', help='use tor proxy', action='store_true')
	args = ap.parse_args()

	query = args.q
	engines = [e.lower().strip() for e in args.e.split(',') if e.strip()]
	proxy = args.p or args.tor
	timeout = config.timeout if not proxy else config.timeout + 10
	search_engines = dict(search_engines)
	search_engines['all'] = All

	if len(engines) == 1 and engines[0] in search_engines: 
		engine = engines[0]
		se = search_engines[engine](proxy, timeout)
		se.search(query, args.m, args.u, True)
		se.report(args.r)
	elif len(engines) > 1 and any(e in search_engines for e in engines):
		se = Multi(engines, proxy, timeout)
		se.search(query, args.m, args.u, True)
		se.report(args.r)
	else: 
		print('Choose a search-engine: '+', '.join(search_engines.keys())) 

