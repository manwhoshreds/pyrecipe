# -*- coding: utf-8 -*-
"""
    pyrecipe.api
    ~~~~~~~~~~~~

    Api class for geting and posting data to openrecipes.

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""

import json

import requests

from pyrecipe.recipe import Recipe
from pyrecipe.shopper import ShoppingList


class RecipeAPI:

    def __init__(self):
        # for accessing out side of lan.
        #self.base_uri = 'https://venus-server.duckdns.org/openRecipes/api'
        #self.base_url = 'http://192.168.0.31/openRecipes/includes/api'
        self.base_url = 'http://localhost/open_recipes/includes/api/recipe/{}.php'

    def _get_url(self, action):
        return self.base_url.format(action)

    def _GET(self, path, params=None):
        return requests.request('GET', path, params=params)

    def _POST(self, path, params=None, payload=None):
        return requests('POST', path, params=params, payload=payload)

    def _DELETE(self, path, params=None, payload=None):
        return self._request('DELETE', path, params=params, payload=payload)

    def read(self):
        """Read data from Open Recipes."""
        self.url += "read.php"
        req =  request.Request(self.url)
        resp = request.urlopen(req)
        js = json.loads(resp.read().decode('utf-8'))
        for item in js['recipes']:
            print(item)
        
    def post(self):
        """Post recipe data to Open Recipes."""
        self.url += "create.php"
        resp =  requests.post(self.url, data=data)
        print(resp.json())
        #js['message'] == "success!" and print('Recipe created') or print('Failed')
    
    def search(self, words):
        url = self._get_url('search')
        print(url)
        payload = {'s': words}
        resp = self._GET(url, words)
        return resp.json()

    def test(self):
        """Post recipe data to Open Recipes."""
        self.url += "create.php"
        data = bytes(urlencode({'user_name': 'manwhoshreds'}).encode())
        print(data)
        req =  request.Request(self.url, data=data)
        resp = request.urlopen(req)
        print(resp.read())
        #js = json.loads(resp.read().decode('utf-8'))
        #js['message'] == "success!" and print('Recipe created') or print('Failed')
        

if __name__ == '__main__':
    api = RecipeAPI()
    search = api.search('dlfjdflksajdflkajsdlfkjasldfjljdfalskdjflk')
    
    print(search)

