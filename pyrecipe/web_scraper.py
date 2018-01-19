# -*- coding: utf-8 -*-
"""
    pyrecipe.web_scraper
    ~~~~~~~~~~~~~~~~~~~~

    The pyrecipe web_scraper module is a web scraping utility
    used to download and analyze recipes found on websites in 
    an attempt to download and save the recipe data in the 
    format understood by pyrecipe.

    - RecipeWebScraper: A web scraper used to save recipes from the internet.
                    
    Currently supported sites: www.geniuskitchen.com

    copyright: 2017 by Michael Miller
    license: GPL, see LICENSE for more details.
"""
from urllib.request import urlopen
import bs4

from pyrecipe.recipe import Recipe
from pyrecipe.ingredient import IngredientParser

class RecipeWebScraper(Recipe):
    
    def __init__(self):
        self.req = None
        self.soup = None
        super().__init__()
        #self.recipe = Recipe()

    def scrape(self, url):
        self['source_url'] = url
        self.req = urlopen(url)
        self.soup = bs4.BeautifulSoup(self.req, 'html.parser')
        self._get_recipe_name() 
        self._get_ingredients()
        self._get_author()
        self._get_method()
        
    def _get_recipe_name(self):
        name_box = self.soup.find('h2', attrs={'class': 'modal-title'})
        self['recipe_name'] = name_box.text.strip()

    def _get_ingredients(self):
        ingred_box = self.soup.find_all('ul', attrs={'class': 'ingredient-list'})
        ingred_parser = IngredientParser(return_dict=True)
        ingredients = []
        for item in ingred_box:
            for litag in item.find_all('li'):
                ingred_text = ' '.join(litag.text.strip().split())
                ingred = ingred_parser.parse(ingred_text)
                ingredients.append(ingred)
        self['ingredients'] = ingredients


    def _get_method(self):
        method_box = self.soup.find('div', attrs={'class': 'directions-inner container-xs'})
        litags = method_box.find_all('li')
        # last litag is "submit a correction", we dont need that
        del litags[-1]
        recipe_steps = []
        for item in litags:
            step_dict = {}
            step_dict['step'] = item.text.strip()
            recipe_steps.append(step_dict)

        self['steps'] = recipe_steps
    
    def _get_author(self):
        name_box = self.soup.find('h6', attrs={'class': 'byline'})
        recipe_by = name_box.text.strip()
        self['author'] = ' '.join(recipe_by.split(' ')[2:]).strip()
        

if __name__ == '__main__':

    scraper = RecipeWebScraper()
    #scraper.scrape('http://www.geniuskitchen.com/recipe/pot-sticker-dipping-sauce-446277')
    #scraper.scrape('http://www.geniuskitchen.com/recipe/bourbon-chicken-45809')
    scraper.scrape('http://www.geniuskitchen.com/recipe/chicken-parmesan-19135')
    #scraper.scrape('http://www.geniuskitchen.com/recipe/stuffed-cabbage-rolls-29451')
    scraper.print_recipe()
    #scraper.recipe.dump()

