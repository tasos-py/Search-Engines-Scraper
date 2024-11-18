class SearchResults(object):
    '''Stores the search results'''
    def __init__(self, items=None):
        self._results = items or []
    
    def links(self):
        '''Returns the links found in search results'''
        return [row.get('link') for row in self._results]
    
    def titles(self):
        '''Returns the titles found in search results'''
        return [row.get('title') for row in self._results]
    
    def text(self):
        '''Returns the text found in search results'''
        return [row.get('text') for row in self._results]
    
    def hosts(self):
        '''Returns the domains found in search results'''
        return [row.get('host') for row in self._results]
    
    def results(self):
        '''Returns all data found in search results'''
        return self._results
    
    def __getitem__(self, index):
        return self._results[index]
    
    def __len__(self):
        return len(self._results)

    def __str__(self):
        return '<SearchResults ({} items)>'.format(len(self._results))
    
    def append(self, item):
        '''appends an item to the results list.'''
        self._results.append(item)
    
    def extend(self, items):
        '''appends items to the results list.'''
        self._results.extend(items)
