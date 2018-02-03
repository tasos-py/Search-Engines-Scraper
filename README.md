# searchengines
Search google, bing, yahoo, and other search engines with python.  

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

## Requirements  
Python 2.7 - 3.6, requests, bs4  

## Installation  
Copy searchengines to your python libraries.  
Install requirements,  
```
python -m pip install -r searchengines\requirements.txt --upgrade
```  

## Usage  
As a library:  

```
from searchengines import *

engine = Google()
results = engine.search("your query")
links = results.links()
```

As a cli script:  

```  
python search.py -e google -q "your query" -r html,csv
```
