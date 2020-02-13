import requests
from .config import PYTHON_VERSION


def quote_url(url):
    '''encodes URLs.'''
    if PYTHON_VERSION == 2:
        url = encode_str(url)
    return requests.utils.quote(url, safe=';/?:@&=+$,#')

def unquote_url(url):
    '''decodes URLs.'''
    if PYTHON_VERSION == 2:
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

