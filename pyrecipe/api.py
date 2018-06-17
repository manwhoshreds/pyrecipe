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


class ShoppingList:
    
    def __init__(self, recipe):
        super().__init__(recipe)

    def _url(path):
        path = 'http://localhost/open_recipes/includes/api/shopping_list/' + path
        return path
    
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
        data = 
        resp =  requests.post(self.url, data=data)
        print(resp.json())
        #js['message'] == "success!" and print('Recipe created') or print('Failed')
    
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
    api = RecipeAPI('korean pork tacos')
    api.post()
    #api.read()
