# -*- coding: utf-8 -*-
"""
    pyrecipe.api
    ~~~~~~~~~~~~

    Api class for geting and posting data to openrecipes.

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""

import json
import urllib.request as request
from urllib.parse import urlencode

from pyrecipe.recipe import Recipe


class RecipeAPI(Recipe):
    
    def __init__(self, recipe):
        self.url = 'http://localhost/open_recipes/includes/api/shopping_list/'
        super().__init__(recipe)
    
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
        data = bytes(urlencode(self['_recipe_data']).encode())
        req =  request.Request(self.url, data=data)
        resp = request.urlopen(req)
        js = json.loads(resp.read().decode('utf-8'))
        js['message'] == "success!" and print('Recipe created') or print('Failed')
    
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
    api.test()
    #api.read()
