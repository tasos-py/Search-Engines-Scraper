from os import path, pardir, name as os_name
from sys import version_info


## Python version 
python_version = version_info.major

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
tor = 'socks5h://127.0.0.1:9150'

base_dir = path.abspath(path.join(path.dirname(path.abspath(__file__)), pardir))

## Path to report files 
report_files_dir = path.join(base_dir, 'reports') + path.sep

