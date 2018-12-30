# -*- encoding: utf-8 -*-

import argparse
from core.engines import *
import config
from lib import windows_cmd_encoding


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-q', help='query', required=True)
    ap.add_argument('-e', help='search engine(s) - ' + ', '.join(search_engines), default='google')
    ap.add_argument('-r', help='report file [html, csv]', default='')
    ap.add_argument('-p', help='number of pages', default=config.max_pages, type=int)
    ap.add_argument('-u', help='unique domains', action='store_true')
    ap.add_argument('-proxy', help='use proxy (protocol://ip:port)', default=config.proxy)
    ap.add_argument('-tor', help='use tor proxy', action='store_true')
    args = ap.parse_args()

    proxy = args.proxy or (config.tor if args.tor else None)
    timeout = config.timeout + (10 * int(args.tor))
    engines = [
        e.strip() for e in args.e.lower().split(',') 
        if e.strip() in search_engines or e.strip() == 'all'
    ]

    if not engines:
        print('Choose a search engine: \n' + ', '.join(search_engines))
    else:
        if 'all' in engines:
            engine = All(proxy, timeout)
        elif len(engines) == 1:
            engine = search_engines[engines[0]](proxy, timeout)
        elif len(engines) > 1:
            engine = Multi(engines, proxy, timeout)

        engine.search(args.q, args.p, args.u)
        engine.report(args.r)


