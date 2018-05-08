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


def search(self, search_str, site='tasty'):
    """ This search function works with tasty.
    I havent figured out how to implement this inside the individual
    web scraper subclasses yet so im leting it hang out until i figuered it out
    """
    search_str = utils.format_text(search_str)
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


class RecipeWebScraper(Recipe):
    """Scrape recipes from a web source.
    
    This is a base class used to scrape a web source.
    Scraped recipes shoul be used as a template for a
    recipe.
    """
    def __new__(cls, url):
        scrapers = {
            'https://tasty.co/': TastyWebScraper,
            'http://www.geniuskitchen.com/': GeniusWebScraper
        }
        cls.scrapeable_sites = list(scrapers.keys())
        scrapeable = [s for s in cls.scrapeable_sites if url.startswith(s)][0]
        if not scrapeable:
            sys.exit(utils.msg(
                "{} is not scrapeable by pyrecipe".format(url), "WARN"))
        
        return scrapers[scrapeable].__new__(cls)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        req = urlopen(self.url)
        self.soup = bs4.BeautifulSoup(req, 'html.parser')


    
    def scrape(self):
        self['source_url'] = self.url
        self['recipe_name'] = self.recipe_name
        self['author'] = self.author
        self.ingredients = self.scraped_ingredients
        self['steps'] = self.scraped_method


class GeniusWebScraper(RecipeWebScraper):
    
    def __new__(cls):
        return object.__new__(GeniusWebScraper)
    
    def __init__(self, url):
        super().__init__(url)
    
    @property
    def recipe_name(self):
        name_box = self.soup.find('h2', attrs={'class': 'modal-title'})
        recipe_name = name_box.text.strip()
        return recipe_name
 
    @property
    def author(self):
        name_box = self.soup.find('h6', attrs={'class': 'byline'})
        recipe_by = name_box.text.strip()
        author = ' '.join(recipe_by.split(' ')[2:]).strip()
        return author
    
    @property
    def scraped_ingredients(self):
        ingred_box = self.soup.find_all('ul', attrs={'class': 'ingredient-list'})
        ingredients = []
        for item in ingred_box:
            for litag in item.find_all('li'):
                ingred = ' '.join(litag.text.strip().split())
                ingredients.append(ingred)
        return ingredients
    
    @property
    def scraped_method(self):
        method_box = self.soup.find('div', attrs={'class': 'directions-inner container-xs'})
        litags = method_box.find_all('li')
        # last litag is "submit a correction", we dont need that del litags[-1]
        recipe_steps = []
        for item in litags:
            step_dict = {}
            step_dict['step'] = item.text.strip()
            recipe_steps.append(step_dict)

        steps = recipe_steps
        return steps


class TastyWebScraper(RecipeWebScraper):
    
    def __new__(cls):
        return object.__new__(TastyWebScraper)
    
    def __init__(self, url):
        super().__init__(url)
    
    @property
    def recipe_name(self):
        """Recipe name."""
        name_box = self.soup.find('h1', attrs={'class': 'recipe-name'})
        recipe_name = name_box.text.strip()
        return recipe_name
 
    @property
    def author(self):
        """Recipe author."""
        author = ''
        name_box = self.soup.find('h3', attrs={'class': 'xs-text-5'})
        if name_box:
            recipe_by = name_box.text.strip()
            author = ' '.join(recipe_by.split('by')).strip()
        return author
    
    @property
    def scraped_ingredients(self):
        """Recipe ingredients."""
        ingred_box = self.soup.find('ul', attrs={'class': 'list-unstyled'})
        ingredients = []
        for litag in ingred_box.find_all('li'):
            ingred = ' '.join(litag.text.strip().split())
            ingredients.append(ingred)
        return ingredients
    
    @property
    def scraped_method(self):
        """Recipe method."""
        method_box = self.soup.find('ol', attrs={'class': 'prep-steps'})
        litags = method_box.find_all('li')
        # Quite often, a recipe site has something unnessasary at the end of 
        # the steps such as Enjoy! or 'submit a correction'. be on the look out
        # for such behavior and uncomment the next line if need be.
        #del litags[-1]
        recipe_steps = []
        for item in litags:
            step_dict = {}
            step_dict['step'] = item.text.strip()
            recipe_steps.append(step_dict)
        return recipe_steps

if __name__ == '__main__':
    test = RecipeWebScraper('https://tasty.co/recipe/one-pan-teriyaki-salmon-dinner')
    print(test.scrapeable_sites)

    test.scrape()
    test.print_recipe()
    #test = RecipeWebScraper()
    #test.search('hamburger')
