from os import path as os_path, pardir as os_pardir, name as os_name
from sys import version_info


## Python version 
python_version = version_info.major

## Maximum number or pages to search
search_pages = 10

## HTTP request timeout 
timeout = 10

## User-Agent string 
user_agent = 'Mozilla/5.0 (Windows NT 6.1; rv:51.0) Gecko/20100101 Firefox/51.0'

## Proxy address 
proxy = None

## TOR proxy address 
tor = 'socks5h://127.0.0.1:9050'

base_dir = os_path.abspath(os_path.dirname(os_path.abspath(__file__)))

## Path to report files 
report_files_dir = os_path.join(base_dir, 'reports') + os_path.sep

