from os import path, pardir
import sys


## Python version 
python_version = sys.version_info.major

## Maximum number or results 
max_links = 100

## Maximum number or pages 
max_pages = 20

## Domains in this list will not be collected 
blacklist = []

## HTTP request timeout 
timeout = 10

## User-Agent string 
user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:51.0) Gecko/20100101 Firefox/51.0'

## Proxy address 
proxy = None

## TOR proxy address 
tor = 'socks5h://127.0.0.1:9050'

base_dir = path.abspath(path.join(path.dirname(path.abspath(__file__)), pardir))
files_dir = path.join(base_dir, 'files') + path.sep

## Path to html report file 
html_file = path.join(files_dir, 'search-report.html')

## Path to html report file 
csv_file = path.join(files_dir, 'search-report.csv')


