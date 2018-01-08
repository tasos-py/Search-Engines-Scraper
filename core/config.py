from os import path, pardir
import sys


''' Python version '''
python_version = sys.version_info.major

''' Maximum number or results '''
max_results = 100

''' Maximum number or pages '''
max_pages = 100

''' Domains in this list will not be collected '''
blacklist = []

''' HTTP request timeout '''
timeout = 10

''' User-Agent string '''
user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:51.0) Gecko/20100101 Firefox/51.0'

''' Proxy addres '''
proxy = None

''' TOR proxy addres ''' 
tor = 'socks5h://127.0.0.1:9150'

this_file = path.abspath(__file__)
base_dir = path.abspath(path.join(path.dirname(this_file), pardir))

''' Path to html report file '''
html_file = path.join(base_dir, 'files', 'search-report.html')

''' Path to html report file '''
csv_file = path.join(base_dir, 'files', 'search-report.csv')

