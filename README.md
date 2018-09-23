# searchengines
A python library that performs queries to google, bing, yahoo, and other search engines. 
When using Torch, `requests[socks]` is required, which can be installed using the requirements.txt file, as described below.

## Search engines  
Google  
Bing  
Yahoo  
Duckduckgo  
Startpage  
Dogpile  
Ask  
Searx  
Torch  

## Features  
Can use one, multiple, or all the search engines listed above.
Proxy support. 
Collects dark web links with Torch.
Creates report files (html, csv).
Easy to add new search engines. You can add a new engine by creating a new class in `searchengines/core/engines.py`, and register it on the `search_engines` dictionary in the same file. The class must be a child of `Search`, and must have those attributes: `_url`, `_title`, `_text`, `_links`, `_next`, and methods: `_first_page`, `_next_page`.

## Requirements  
Python 2.7 - 3.6, with requests and bs4  

## Installation  
Copy searchengines to your python libraries  
Install requirements,  `python -m pip install -r searchengines/requirements.txt --upgrade`  

## Usage  
As a library:  

```
from searchengines import *

engine = Google()
results = engine.search("my query")
links = results.links()

print(links)
```

As a cli script:  

```  
python searchengines/search.py -e google -q "your query" -r html,csv
```
