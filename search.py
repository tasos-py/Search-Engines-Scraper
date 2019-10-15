# -*- encoding: utf-8 -*-
import argparse

try:
    from search_engines.core.engines import engines_dict, Multi, All
    from search_engines import config
    from search_engines.libs import windows_cmd_encoding
except ImportError as e:
    msg = '"{}"\nPlease install `search_engines` to resolve this error.'
    raise ImportError(msg.format(e.__doc__))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-q', help='query', required=True)
    ap.add_argument('-e', help='search engine(s) - ' + ', '.join(engines_dict), default='google')
    ap.add_argument('-r', help='report file [html, csv, json]', default=None)
    ap.add_argument('-p', help='number of pages', default=config.search_pages, type=int)
    ap.add_argument('-f', help='filter results [url, title, text, host]', default=None)
    ap.add_argument('-u', help='collect only unique links', action='store_true')
    ap.add_argument('-proxy', help='use proxy (protocol://ip:port)', default=config.proxy)
    ap.add_argument('-tor', help='use tor proxy', action='store_true')
    args = ap.parse_args()

    proxy = args.proxy or (config.tor if args.tor else None)
    timeout = config.timeout + (10 * int(args.tor))
    engines = [
        e.strip() for e in args.e.lower().split(',') 
        if e.strip() in engines_dict or e.strip() == 'all'
    ]

    if not engines:
        print('Choose a search engine: \n' + ', '.join(engines_dict))
    else:
        if 'all' in engines:
            engine = All(proxy, timeout)
        elif len(engines) > 1:
            engine = Multi(engines, proxy, timeout)
        else:
            engine = engines_dict[engines[0]](proxy, timeout)

        engine.unique_urls = args.u
        if args.f:
            engine.set_search_operator(args.f)
        engine.search(args.q, args.p)
        engine.report(args.r)

