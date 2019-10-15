# search_engines  

A python library that queries Google, Bing, Yahoo, and other search engines and collects the search results.  
Note that web-scraping may be against the TOS of some search engines, and may result in a temporary ban.

## Supported search engines  

_Google_  
_Bing_  
_Yahoo_  
_Duckduckgo_  
_Startpage_  
_Dogpile_  
_Ask_  
_Searx_  
_Aol_  
_Torch_  

## Features  

 - Creates report files (html, csv, json).  
 - Supports advanced search operators (`url`, `title`, `text`).  
 - HTTP and SOCKS proxy support.  
 - Collects dark web links with Torch.  
 - Easy to add new search engines. You can add a new engine by creating a new class in `search_engines/core/engines.py` and register it in `engines_dict`, in the same file. The new class should subclass `Search`, and override the following methods: `_selectors`, `_first_page`, `_next_page` and have the following attributes: `_name`, `_base_url`. 
 - Python2 - Python3 compatible.  

## Requirements  

_Python 2.7 - 3.7_ with  
_[Requests](http://docs.python-requests.org/en/master/)_ and  
_[BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)_  

## Installation  

Run the setup file: `$ python setup.py install`.  
Done!  

## Usage  

As a library:  

```
from search_engines import Google

engine = Google()
results = engine.search("my query")
links = results.links()

print(links)
```

As a CLI script:  

```  
$ python search.py -e google,bing -q "my query" -r html,csv
```
