# -*- encoding: utf-8 -*-

import argparse
from core.engines import *
from core import config
from core.utilities import decode_argv


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-q', help='query', required=True)
    ap.add_argument('-e', help='search engine(s) - ' + ', '.join(search_engines), default='google')
    ap.add_argument('-r', help='report file [html, csv]', default='')
    ap.add_argument('-p', help='number of pages', default=config.max_pages, type=int)
    ap.add_argument('-u', help='unique results', action='store_true')
    ap.add_argument('-proxy', help='use proxy (scheme://ip:port)', default=config.proxy)
    ap.add_argument('-tor', help='use tor proxy', action='store_true')
    args = ap.parse_args()
    
    query = decode_argv(args.q)
    engines = [e.strip() for e in args.e.lower().split(',') if e.strip()]
    proxy = args.proxy or (config.tor if args.tor else None)
    timeout = config.timeout + (10 * int(args.tor))
    all_engines = dict(search_engines)
    all_engines['all'] = All

    if len(engines) == 1 and engines[0] in all_engines:
        engine = engines[0]
        se = all_engines[engine](proxy, timeout)
        se.search(query, args.p, args.u)
        se.report(args.r)
    elif len(engines) > 1 and any(e in all_engines for e in engines):
        se = Multi(engines, proxy, timeout)
        se.search(query, args.p, args.u)
        se.report(args.r)
    else:
        print('Choose a search engine: \n' + ', '.join(search_engines)) 

