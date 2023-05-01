from ..engine import SearchEngine
from ..config import PROXY, TIMEOUT, FAKE_USER_AGENT, APPLICATION_JSON
from ..utils import unquote_url
import json
from ..results import SearchResults

class SemanticSchoolar(SearchEngine):
    '''Searches google.com'''
    def __init__(self, proxy=PROXY, timeout=TIMEOUT):
        super(SemanticSchoolar, self).__init__(proxy, timeout, self._parse_response)
        print("SemanticSchoolar")
        self._base_url = 'https://www.semanticscholar.org/api/1/search'
        self._data = {
            "queryString": "",
            "page": 1,
            "pageSize": 10,
            "sort": "relevance",
            "authors": [],
            "coAuthors": [],
            "venues": [],
            "yearFilter": None,
            "requireViewablePdf": False,
            "fieldsOfStudy": ["medicine", "biology"],
            "useFallbackRankerService": False,
            "useFallbackSearchCluster": False,
            "hydrateWithDdb": True,
            "includeTldrs": True,
            "performTitleMatch": True,
            "includeBadges": False,
            "getQuerySuggestions": False
        }   
        self._delay = (2, 6)
        self._current_page = 1
        self.set_headers({'User-Agent':FAKE_USER_AGENT, 'Content-Type': APPLICATION_JSON})
    
    def _first_page(self):
        '''Returns the initial page and query.'''
        print("self._query", self._query)
        url = self._base_url
        self._data['queryString'] = self._query
        data = json.dumps(self._data)
        return {'url':url, 'data':data}
    
    def _next_page(self, tags):
        '''Returns the next page URL and post data (if any)'''
        print("next_page")
        self._current_page += 1
        data = self._data['page']
        data['page'] = self._current_page
        url = self._base_url
        data = json.dumps(self._data)
        return {'url':url, 'data':data}

    def _parse_response(self, response):
        json_response = json.loads(response.html)
        items = []
        if 'results' in json_response:
            for result in json_response['results']:
                items.append({
                    'title': result['title']['text'],
                    'text': result['paperAbstract']['tldr'] if 'tldr' in result['paperAbstract'] else result['paperAbstract']['text'] ,
                    'url': result['primaryPaperLink']['url']
                })
            self.results = SearchResults(items)
            return 
        raise Exception('Error parsing response')
