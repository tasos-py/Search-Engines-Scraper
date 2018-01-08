# searchengines
Search google, bing, yahoo, and other search engines with python.  

# Search engines:  
Google  
Bing  
Yahoo  
Duckduckgo  
Startpage  
Dogpile  
Ask  
Searx  
Torch  

# Requirements:  
Python 2.7 - 3.6, requests, bs4  

# Installation:  
Copy `searchengines` to Python\Lib\site-packages\
Run `python -m pip install -r searchengines\requirements.txt`  

## Usage:  
As a library:  

<code>
  import searchengines
  
  google = searchengines.Google()
  google.search("your query")
  results = google.results
</code>

As a cli script:  

<code>
  python cli.py -e google -q "your query" -r html,csv
<code>
