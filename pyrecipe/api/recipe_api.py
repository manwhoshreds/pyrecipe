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

    def __init__(self, debug=False):
        # for accessing out side of lan.
        #self.base_uri = 'http://venus-server.duckdns.org/openRecipes/api/recipe/{}.php'
        self.base_url = 'http://192.168.0.31/openRecipes/includes/api/recipe/{}.php'
        self.debug = debug
        #self.base_url = 'http://localhost/open_recipes/includes/api/recipe/{}.php'

    def _get_url(self, action):
        return self.base_url.format(action)

    def read_one(self, recipe):
        """Read data from Open Recipes."""
        url = self._get_url('read_one')
        payload = {'recipe': recipe}
        resp =  requests.get(url, params=payload)
        if self.debug:
            return resp.text
        return resp.json()
        
    def read(self):
        """Read data from Open Recipes."""
        url = self._get_url('read')
        resp =  requests.get(url)
        if self.debug:
            return resp.text
        return resp.json()
    
    def create(self, recipe):
        """Post recipe data to Open Recipes."""
        url = self._get_url('create')
        resp =  requests.post(url, data=recipe)
        if self.debug:
            return resp.text
        return resp.json()
    
    def search(self, words):
        """Search recipes from Open Recipes."""
        url = self._get_url('search')
        payload = {'s': words}
        resp =  requests.get(url, params=payload)
        if self.debug:
            return resp.text
        return resp.json()


if __name__ == '__main__':
    api = RecipeAPI()
    r = Recipe('pesto')
    test = api.create(r)
    #r = Recipe(test)
    #r.print_recipe()
