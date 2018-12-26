from __future__ import print_function

import requests
import csv
import io
from sys import stdout, getfilesystemencoding
from . import config


class Http:
    '''Performs HTTP requests.'''
    def __init__(self, timeout=config.timeout, proxy=config.proxy):
        self.http = requests.session()
        self.timeout = timeout
        self.http.proxies = self._set_proxy(proxy)
        self.http.headers['User-Agent'] = config.user_agent

    def get(self, page, ref=None):
        '''GET request.'''
        try:
            req = self.http.get(
                quote_url(page), headers = {'Referer': quote_url(ref or page)}, 
                timeout = self.timeout
            )
        except requests.exceptions.RequestException as e:
            return {'http':0, 'html':e.__doc__}
        return {'http':req.status_code, 'html':req.text}
    
    def post(self, page, data, ref=None):
        '''POST request.'''
        try:
            req = self.http.post(
                quote_url(page), data, headers = {'Referer': quote_url(ref or page)}, 
                timeout = self.timeout
            )
        except requests.exceptions.RequestException as e:
            return {'http':0, 'html':e.__doc__}
        return {'http':req.status_code, 'html':req.text}
    
    def set_user_agent(self, ua_string):
        '''Sets the User-Agent string.'''
        self.http.headers['User-Agent'] = ua_string
    
    def _set_proxy(self, proxy):
        '''Returns HTTP, HTTPS, SOCKS proxies dictionary.'''
        if proxy:
            if not is_url(proxy):
                print('Warning: Invalid proxy format!')
            proxy = {'http':proxy, 'https':proxy}
        return proxy


def quote_url(url):
    '''encodes URLs.'''
    if config.python_version == 2:
        url = encode_str(url)
    return requests.utils.quote(url, safe=';/?:@&=+$,#')

def unquote_url(url):
    '''decodes URLs.'''
    if config.python_version == 2:
        url = encode_str(url)
    return decode_bytes(requests.utils.unquote(url))

def is_url(link):
    '''Checks if link is URL'''
    parts = requests.utils.urlparse(link)
    return bool(parts.scheme and parts.netloc)

def domain(url):
    '''Returns domain form URL'''
    host = requests.utils.urlparse(url).netloc
    return host.lower().split(':')[0].replace('www.', '')

def encode_str(s, encoding='utf-8', errors='replace'):
    '''Encodes unicode to str - str to bytes.'''
    return s if type(s) is bytes else s.encode(encoding, errors=errors)

def decode_bytes(s, encoding='utf-8', errors='replace'):
    '''Decodes bytes to str, str to unicode.'''
    return s.decode(encoding, errors=errors) if type(s) is bytes else s


class Html:
    '''HTML templates.'''
    html = u'''<html>
    <head>
    <meta charset="UTF-8">
    <title>Search Report</title>
    <style>
    body {{ background-color:#f5f5f5; font-family:Italic, Charcoal, sans-serif; }} 
    a:link {{ color: #262626; }} 
    a:visited {{ color: #808080; }} 
    th {{ font-size:17px; text-align:left; padding:3px; font-style: italic; }} 
    td {{ font-size:14px; text-align:left; padding:1px; }} 
    </style>
    </head>
    <body>
    <table>
    <tr><th>Query: '{query}'</th></tr>
    <tr><td> </td></tr>
    </table>
    {table}
    </body>
    </html>
    '''
    
    table = u'''<table>
    <tr><th>{engine} search results </th></tr>
    </table>
    <table>
    {rows}
    </table>
    <br>
    '''
    
    row = u'''<tr>
    <td>{number})</td>
    <td><a href="{link}" target="_blank">{link}</a></td>
    {data}
    </tr>
    '''
    
    data = u'''<tr><td></td><td>{}</td></tr>'''


def results_print(engines):
    '''Prints the results.'''
    for engine in engines:
        console(engine._name + ' results') 
        for i,v in enumerate(engine.results, 1):
            v = v['link']
            if config.python_version == 2:
                v = encode_str(v) 
            console('{:<3}{}'.format(i, v)) 
        console(' ')

def results_html(engines):
    '''Creates html report.'''
    query = decode_bytes(engines[0].query) if engines else ''
    tables = u''
    for engine in engines:
        rows = u''
        for i, v in enumerate(engine.results, 1):
            data = u''
            if 'title' in engine.filter:
                data += Html.data.format(v['title'])
            elif 'text' in engine.filter:
                data += Html.data.format(v['text'])
            rows += Html.row.format(number=i, link=v['link'], data=data)
        tables += Html.table.format(engine=engine._name, rows=rows) 
    return Html.html.format(query=query, table=tables)

def results_csv(engines):
    '''Creates csv report.'''
    encoder = decode_bytes if config.python_version == 3 else encode_str
    data = [['Query', 'Engine', 'Domain', 'URL', 'Title', 'Text']]
    for engine in engines:
        for i in engine.results:
            row = [
                engine.query, engine._name, 
                i['host'], i['link'], i['title'], i['text']
            ]
            row = [encoder(i) for i in row]
            data.append(row)
    return data

def write_file(data, path, encoding='utf-8'):
    '''Creates report files.'''
    try:
        if config.python_version == 2 and type(data) is list:
            f = io.open(path, 'wb') 
        else: 
            f = io.open(path, 'w', encoding=encoding, newline='')
        if type(data) is list:
            writer = csv.writer(f)
            writer.writerows(data)
        else:
            f.write(data)
        f.close()
        console(u'Report file: ' + path)
    except IOError as e:
        print(e)

def console(msg, end=u'\r\n'):
    '''Prints data on the console.'''
    msg = decode_bytes(msg)
    if config.python_version == 2 and config.os_name == 'nt':
        msg = decode_bytes(encode_str(msg, 'ascii'))
    print(msg, end=end)

def decode_argv(arg):
    '''Decodes command line arguments.'''
    encoding = getfilesystemencoding()
    return decode_bytes(arg, encoding)



