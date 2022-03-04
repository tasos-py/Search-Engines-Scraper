# search_engines  
A Python library that queries Google, Bing, Yahoo and other search engines and collects the results from multiple search engine results pages.  
Please note that web-scraping may be against the TOS of some search engines, and may result in a temporary ban.

## Supported search engines  

_[Google](https://www.google.com)_  
_[Bing](https://www.bing.com)_  
_[Yahoo](https://search.yahoo.com)_  
_[Duckduckgo](https://duckduckgo.com)_  
_[Startpage](https://www.startpage.com)_  
_[Aol](https://search.aol.com)_  
_[Dogpile](https://www.dogpile.com)_  
_[Ask](https://uk.ask.com)_  
_[Mojeek](https://www.mojeek.com)_  
_[Torch](http://xmh57jrzrnw6insl.onion/4a1f6b371c/search.cgi)_  

## Features  

 - Creates output files (html, csv, json).  
 - Supports search filters (url, title, text).  
 - HTTP and SOCKS proxy support.  
 - Collects dark web links with Torch.  
 - Easy to add new search engines. You can add a new engine by creating a new class in `search_engines/engines/` and add it to the  `search_engines_dict` dictionary in `search_engines/engines/__init__.py`. The new class should subclass `SearchEngine`, and override the following methods: `_selectors`, `_first_page`, `_next_page`. 
 - Python2 - Python3 compatible.  
 - Now also supports getting URLs from Image Searches for images. Still experimental!
 - You can use a randomly generated fake useragent to attempt to improve search engine scraping success
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

If you'd like to use a randomly generated useragent:

```
from search_engines import Startpage

engine=Startpage(fakeagent=True)
results=engine.search("my query")
links=results.links()

print(links)



```


If you're looking to get images:

```
from search_engines import Yahoo

engine = Yahoo() #highly recommended to use fakeagent=True
results=engine.search("cat",searchtype="image")
links=results.links()

print(links)


```
***Note that you probably will not get many images for now, as pagination is still a work-in-progress***


Currently the following Engines are supported for image search:
* Yahoo
* Bing
* AOL
* Qwant ** temperamental even with fakeagent
* Mojeek ** works well with fakeagent flag thrown, and has pagination!
* Google ** temperamental even with fakeagent

As a CLI script:  

```  
$ python search_engines_cli.py -e google,bing -q "my query" -o json,print
```

## Other versions  

 - [async-search-scraper](https://github.com/soxoj/async-search-scraper) A really cool asynchronous implementation, written by @soxoj   
