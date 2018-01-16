# -*- coding: utf-8 -*-
"""
    pyrecipe.web_scraper
    ~~~~~~~~~~~~~~~~~~~~

    The pyrecipe web_scraper module is a web scraping utility
    used to download and analyze recipes found on websites in 
    an attempt to download and save the recipe data in the 
    format understood by pyrecipe.

    - RecipeWebScraper:

    copyright: 2017 by Michael Miller
    license: GPL, see LICENSE for more details.
"""
from urllib.request import urlopen
import bs4

from pyrecipe import Recipe, IngredientParser
from pyrecipe.ingredient import IngredientParser

class RecipeWebScraper:
    
    def __init__(self):
        self.url = ''
        self.req = None
        self.soup = None
        self.recipe = Recipe()

    def scrape(self, url):
        self.url = url
        self.req = urlopen(self.url)
        self.soup = bs4.BeautifulSoup(self.req, 'html.parser')
        self._get_recipe_name() 
        self.get_ingredients()
        self._get_author()
        self._get_method()
        
    def _get_recipe_name(self):
        name_box = self.soup.find('h2', attrs={'class': 'modal-title'})
        self.recipe['recipe_name'] = name_box.text.strip()

    def get_ingredients(self):
        ingred_box = self.soup.find_all('ul', attrs={'class': 'ingredient-list'})
        ingred_parser = IngredientParser(return_dict=True)
        ingredients = []
        for item in ingred_box:
            for litag in item.find_all('li'):
                ingred_text = ' '.join(litag.text.strip().split())
                ingred = ingred_parser.parse(ingred_text)
                ingredients.append(ingred)

        self.recipe['ingredients'] = ingredients


    def _get_method(self):
        method_box = self.soup.find('div', attrs={'class': 'directions-inner container-xs'})
        litags = method_box.find_all('li')
        recipe_steps = []
        for item in litags:
            step_dict = {}
            step_dict['step'] = item.text.strip()
            recipe_steps.append(step_dict)

        self.recipe['steps'] = recipe_steps
    
    def _get_author(self):
        name_box = self.soup.find('h6', attrs={'class': 'byline'})
        recipe_by = name_box.text.strip()
        self.recipe['author'] = ' '.join(recipe_by.split(' ')[2:]).strip()
        

if __name__ == '__main__':

    scraper = RecipeWebScraper()
    scraper.scrape('http://www.geniuskitchen.com/recipe/pot-sticker-dipping-sauce-446277')
    #scraper.scrape('http://www.geniuskitchen.com/recipe/bourbon-chicken-45809')
    print(scraper.recipe.dump())

