# -*- encoding: UTF-8 -*-
"""
    pyrecipe.webscraper
    ~~~~~~~~~~~~~~~~~~~
    The recipe module contains the main recipe
    class used to interact with ORF (open recipe format) files.
    You can simply print the recipe or print the xml dump.

    - RecipeWebScraper: The pyrecipe web_scraper class is a web
                        scraping utility used to download and analyze
                        recipes found on websites in an attempt to
                        save the recipe data in the format understood
                        by pyrecipe.
                        Currently supported sites: www.geniuskitchen.com
    * Inherits from Recipe

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""
import sys
from urllib.request import urlopen
from urllib.parse import urlencode

import bs4

import pyrecipe.utils as utils
from pyrecipe import (Recipe, IngredientParser)

class RecipeWebScraper(Recipe):
    """Scrape recipes from a web source.
    
    This is a base class used to scrape a web source.
    Scraped recipes shoul be used as a template for a
    recipe.
    """
    def __init__(self):
        super().__init__()
    
    def search(self, search_str, site='tasty'):
        site = site.lower()
        base_urls = {
            'tasty': 'https://tasty.co/search?'
        }
        try:
            base_url = base_urls[site]
        except KeyError:
            sys.exit(utils.msg(
                "Site is not searchable from pyrecipe", level="ERROR")
            )
        
        encoded_search = urlencode({"q": search_str})
        search = "{}{}".format(base_url, encoded_search)
        req = urlopen(search)
        soup = bs4.BeautifulSoup(req, 'html.parser')
        
        # feed-item corresponds to link items from the search
        search_results = soup.find_all('a', attrs={'class': 'feed-item'})
        
        results = {}
        for item in search_results:
            url = item.get('href')
            name = url.split('/')[-1].replace("-", " ").title()
            results[name] = url
        
        return results
    
    def scrape(self, url):
        try:
            self.req = urlopen(url)
        except ValueError:
            sys.exit('You must supply a valid url.')
        self.soup = bs4.BeautifulSoup(self.req, 'html.parser')
        self._fetch_recipe_name()
        self._fetch_ingredients()
        self._fetch_author()
        self._fetch_method()
    
    def _fetch_recipe_name(self):
        name_box = self.soup.find('h2', attrs={'class': 'modal-title'})
        self['recipe_name'] = name_box.text.strip()

    def _fetch_ingredients(self):
        ingred_box = self.soup.find_all('ul', attrs={'class': 'ingredient-list'})
        ingred_parser = IngredientParser()
        ingredients = []
        for item in ingred_box:
            for litag in item.find_all('li'):
                ingred_text = ' '.join(litag.text.strip().split())
                ingred = ingred_parser.parse(ingred_text)
                ingredients.append(ingred)
        self['ingredients'] = ingredients

    def _fetch_method(self):
        method_box = self.soup.find('div', attrs={'class': 'directions-inner container-xs'})
        litags = method_box.find_all('li')
        # last litag is "submit a correction", we dont need that del litags[-1]
        recipe_steps = []
        for item in litags:
            step_dict = {}
            step_dict['step'] = item.text.strip()
            recipe_steps.append(step_dict)

        self['steps'] = recipe_steps

    def _fetch_author(self):
        name_box = self.soup.find('h6', attrs={'class': 'byline'})
        recipe_by = name_box.text.strip()
        self['author'] = ' '.join(recipe_by.split(' ')[2:]).strip()

        

if __name__ == '__main__':
    test = RecipeWebScraper()
    search = test.search("test")
    print(bool(search))
    for key, value in search.items():
        print("{}: {}".format(key, value))
    
    
