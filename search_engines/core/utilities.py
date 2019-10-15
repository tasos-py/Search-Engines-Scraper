from __future__ import print_function
import requests
import csv
import json
import io
from collections import namedtuple

from ..libs import windows_cmd_encoding
from .. import config


class Http:
    '''Performs HTTP requests.'''
    def __init__(self, timeout=config.timeout, proxy=config.proxy):
        self.client = requests.session()
        self.timeout = timeout
        self.client.proxies = self._set_proxy(proxy)
        self.client.headers['User-Agent'] = config.user_agent
        self.response = namedtuple('response', ['http', 'html'])

    def get(self, page, ref=None):
        '''GET request.'''
        headers = {'Referer': self._quote(ref or page)}
        try:
            req = self.client.get(
                self._quote(page), headers=headers, timeout=self.timeout
            )
        except requests.exceptions.RequestException as e:
            return self.response(http=0, html=e.__doc__)
        return self.response(http=req.status_code, html=req.text)
    
    def post(self, page, data, ref=None):
        '''POST request.'''
        headers = {'Referer': self._quote(ref or page)}
        try:
            req = self.client.post(
                quote_url(page), data, headers=headers, timeout=self.timeout
            )
        except requests.exceptions.RequestException as e:
            return self.response(http=0, html=e.__doc__)
        return self.response(http=req.status_code, html=req.text)
    
    def _quote(self, url):
        '''URL-encodes URLs.'''
        if decode_bytes(unquote_url(url)) == decode_bytes(url):
            url = quote_url(url)
        return url
    
    def _set_proxy(self, proxy):
        '''Returns HTTP, HTTPS, SOCKS proxies dictionary.'''
        if proxy:
            if not is_url(proxy):
                raise ValueError('Invalid proxy format!')
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
    '''Encodes unicode to str, str to bytes.'''
    return s if type(s) is bytes else s.encode(encoding, errors=errors)

def decode_bytes(s, encoding='utf-8', errors='replace'):
    '''Decodes bytes to str, str to unicode.'''
    return s.decode(encoding, errors=errors) if type(s) is bytes else s


class Html:
    '''HTML template.'''
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


def print_results(engines):
    '''Prints the results.'''
    for engine in engines:
        console(engine._name + u' results') 
        for i, v in enumerate(engine.results, 1):
            console(u'{:<4}{}'.format(i, v['link'])) 
        console(u' ')

def html_results(engines):
    '''Creates html report.'''
    query = decode_bytes(engines[0]._query) if engines else ''
    tables = u''
    for engine in engines:
        rows = u''
        for i, v in enumerate(engine.results, 1):
            data = u''
            if 'title' in engine._filter:
                data += Html.data.format(v['title'])
            elif 'text' in engine._filter:
                data += Html.data.format(v['text'])
            rows += Html.row.format(number=i, link=v['link'], data=data)
        tables += Html.table.format(engine=engine._name, rows=rows) 
    return Html.html.format(query=query, table=tables)

def csv_results(engines):
    '''Creates csv report.'''
    encoder = decode_bytes if config.python_version == 3 else encode_str
    data = [['Query', 'Engine', 'Domain', 'URL', 'Title', 'Text']]
    for engine in engines:
        for i in engine.results:
            row = [
                engine._query, engine._name, 
                i['host'], i['link'], i['title'], i['text']
            ]
            row = [encoder(i) for i in row]
            data.append(row)
    return data

def json_results(engines):
    '''Creates json report.'''
    jobj = {se._name: [i for i in se.results] for se in engines}
    return json.dumps(jobj)


def write_file(data, path, encoding='utf-8'):
    '''Creates report files.'''
    try:
        if config.python_version == 2 and type(data) in (list, str):
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
        console(e, level=Level.error)

def console(msg, end=u'\r\n', level=None):
    '''Prints data on the console.'''
    print(u'{}{}'.format(level or u'', msg), end=end)

Level = namedtuple('Level', ['info', 'warning', 'error'])(
    info = u'Info: ',
    warning = u'Warning: ',
    error = u'Error: '
)

