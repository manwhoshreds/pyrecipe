# -*- encoding: UTF-8 -*-
"""
    pyrecipe.webscraper
    ~~~~~~~~~~~~~~~~~~~
    The recipe webscraper class lets you download recipes from some sites.
    You can either keep the recipe the way it is and just use it with pyrecipe
    or you can use the recipe as a template for your own recpipe development.

    - WebScraper: The pyrecipe web_scraper class is a web
                  scraping utility used to download and analyze
                  recipes found on websites in an attempt to
                  save the recipe data in the format understood
                  by pyrecipe. This class is a factory that returns
                  webscrapers based on the url given. For a list of
                  currently supported sites, look at the scrapers dict.

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""
import sys

import requests
import bs4
from termcolor import colored

import pyrecipe.utils as utils

#TODO: add property for scraping named ingredients
class RecipeWebScraper:
    """Factory for webscrapers."""

    @staticmethod
    def scrape(url):
        scrapers = {
            'https://tasty.co/': TastyWebScraper,
            'http://www.geniuskitchen.com/': GeniusWebScraper
        }
        scrapeable_sites = list(scrapers.keys())
        try:
            scrapeable = [s for s in scrapeable_sites if url.startswith(s)][0]
        except IndexError:
            # url is not among those listed as scrapeable
            sites = '\n\t'.join(scrapeable_sites)
            sys.exit(utils.msg(
                "{} is not scrapeable by pyrecipe. Please select from the "
                "following sites:\n\n\t".format(url), "WARN") + 
                     utils.msg(sites))

        return scrapers[scrapeable](url).data


class GeniusWebScraper:
    """Web Scraper for http://www.geniuskitchen.com."""

    def __init__(self, url):
        self.data = {}
        self.source_url = url
        req = requests.get(self.source_url).text
        self.soup = bs4.BeautifulSoup(req, 'html.parser')
        self.scrape()

    def scrape(self):
        self.data['name'] = self.scrape_name()
        self.data['author'] = self.scrape_author()
        self.data['ingredients'] = self.scrape_ingredients()
        self.data['steps'] = self.scrape_method()
        self.data['dish_type'] = 'main'

    def scrape_name(self):
        """Recipe name."""
        name_box = self.soup.find('h2', attrs={'class': 'modal-title'})
        recipe_name = name_box.text.strip()
        return recipe_name

    def scrape_author(self):
        """Author."""
        name_box = self.soup.find('h6', attrs={'class': 'byline'})
        recipe_by = name_box.text.strip()
        author = ' '.join(recipe_by.split(' ')[2:]).strip()
        return author

    def scrape_ingredients(self):
        """Ingredients."""
        attrs = {'class': 'ingredient-list'}
        ingred_box = self.soup.find_all('ul', attrs=attrs)
        ingredients = []
        for item in ingred_box:
            for litag in item.find_all('li'):
                ingred = ' '.join(litag.text.strip().split())
                ingredients.append(ingred)
        return ingredients

    def scrape_method(self):
        """Method."""
        attrs = {'class': 'directions-inner container-xs'}
        method_box = self.soup.find('div', attrs=attrs)
        litags = method_box.find_all('li')
        # last litag is "submit a correction", we dont need that
        del litags[-1]
        recipe_steps = []
        for item in litags:
            step_dict = {}
            step_dict['step'] = item.text.strip()
            recipe_steps.append(step_dict)

        steps = recipe_steps
        return steps

    def search(self):
        """Search the site for recipe."""
        # Not implemented yet
        return

class TastyWebScraper:
    """Web Scraper for http://www.tasty.co."""

    def __init__(self, url):
        self.data = {}
        self.source_url = url
        req = requests.get(self.source_url).text
        self.soup = bs4.BeautifulSoup(req, 'html.parser')
        self.scrape()

    def scrape(self):
        """Scrape the recipe."""
        self.data['name'] = self.scrape_name()
        self.data['author'] = self.scrape_author()
        self.data['ingredients'] = self.scrape_ingredients()
        self.data['steps'] = self.scrape_method()
        self.data['dish_type'] = 'main'

    def scrape_name(self):
        """Recipe name."""
        recipe_name = ""
        name_box = self.soup.find('h1', attrs={'class': 'recipe-name'})
        if name_box:
            recipe_name = name_box.text.strip()
        return recipe_name

    def scrape_author(self):
        """Recipe author."""
        author = ''
        name_box = self.soup.find('h3', attrs={'class': 'xs-text-5'})
        if name_box:
            recipe_by = name_box.text.strip()
            author = ' '.join(recipe_by.split('by')).strip()
        return author

    def scrape_ingredients(self):
        """Recipe ingredients."""
        ingred_box = self.soup.find('ul', attrs={'class': 'list-unstyled'})
        ingredients = []
        for litag in ingred_box.find_all('li'):
            ingred = ' '.join(litag.text.strip().split())
            ingredients.append(ingred)
        return ingredients

    def scrape_method(self):
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

    def search(self, search_str, site='tasty'):
        """ This search function works with tasty.

        I havent figured out how to implement this inside the individual
        web scraper subclasses yet so im leting it hang out until i figuered
        it out
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
            if name == '{{ Slug }}':
                break
            results[name] = url

        return results

if __name__ == '__main__':
    from pyrecipe.recipe import Recipe
    test = RecipeWebScraper.scrape("https://tasty.co/recipe/honey-roasted-bbq-pork-char-siu")
    r = Recipe(test)
    r.print_recipe()
