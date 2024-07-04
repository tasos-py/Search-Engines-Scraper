# -*- encoding: utf-8 -*-
import argparse

try:
    from search_engines.engines import search_engines_dict
    from search_engines.multiple_search_engines import MultipleSearchEngines, AllSearchEngines
    from search_engines import config
except ImportError as e:
    msg = '"{}"\nPlease install `search_engines` to resolve this error.'
    raise ImportError(msg.format(str(e)))


def main():
    """
    Main function to handle command-line arguments and perform the search using specified search engines.
    
    This function:
    - Parses command-line arguments using argparse.
    - Sets up proxy and timeout settings.
    - Validates and processes the specified search engines.
    - Configures the search engine(s) based on the provided arguments.
    - Executes the search with the provided query and number of pages.
    - Outputs the search results in the specified format.
    
    Usage:
    -q : Specifies the search query (required).
    -e : Specifies the search engine(s) to use. Can be a comma-separated list or "all". Default is "google".
    -o : Specifies the output file format ("html", "csv", "json") or "print" (default).
    -n : Specifies the filename for the output file. Default is config.OUTPUT_DIR + "output".
    -p : Specifies the number of pages of search results to retrieve. Default is config.SEARCH_ENGINE_RESULTS_PAGES.
    -f : Specifies how to filter search results ("url", "title", "text", "host").
    -i : Flag to ignore duplicate URLs in the search results when using multiple search engines.
    -proxy : Specifies a proxy server to use for the search requests (format: protocol://ip:port). Default is config.PROXY.
    """
    
    ap = argparse.ArgumentParser()
    ap.add_argument('-q', help='query (required)', required=True)
    ap.add_argument('-e', help='search engine(s) - ' + ', '.join(search_engines_dict) + ' (default: "google")', default='google')
    ap.add_argument('-o', help='output file [html, csv, json] (default: print)', default='print')
    ap.add_argument('-n', help='filename for output file', default=config.OUTPUT_DIR+'output')
    ap.add_argument('-p', help='number of pages', default=config.SEARCH_ENGINE_RESULTS_PAGES, type=int)
    ap.add_argument('-f', help='filter results [url, title, text, host]')
    ap.add_argument('-i', help='ignore duplicates, useful when multiple search engines are used', action='store_true')
    ap.add_argument('-proxy', help='use proxy (protocol://ip:port)', default=config.PROXY)
    
    args = ap.parse_args()

    proxy = args.proxy
    timeout = config.TIMEOUT + (10 * bool(proxy))
    engines = [
        e.strip() for e in args.e.lower().split(',') 
        if e.strip() in search_engines_dict or e.strip() == 'all'
    ]

    if not engines:
        print('Please choose a search engine: ' + ', '.join(search_engines_dict))
    else:
        if 'all' in engines:
            engine = AllSearchEngines(proxy, timeout)
        elif len(engines) > 1:
            engine = MultipleSearchEngines(engines, proxy, timeout)
        else:
            engine = search_engines_dict[engines[0]](proxy, timeout)

        engine.ignore_duplicate_urls = args.i
        if args.f:
            engine.set_search_operator(args.f)
        
        engine.search(args.q, args.p)
        engine.output(args.o, args.n)

if __name__ == '__main__':
    """
    If the script is executed directly, call the main function.
    
    This ensures the script can be used both as an importable module and a standalone script.
    """
    main()
