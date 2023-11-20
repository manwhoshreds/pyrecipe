# -*- encoding: UTF-8 -*-
"""
    pyrecipe.webscraper
    ~~~~~~~~~~~~~~~~~~~
    The recipe webscraper class lets you download recipes from some sites.
    You can either keep the recipe the way it is and just use it with pyrecipe
    or you can use the recipe as a template for your own recipe development.

    - RecipeWebScraper: The pyrecipe web_scraper class is a web
                        scraping utility used to download and analyze
                        recipes found on websites in an attempt to
                        save the recipe data in the format understood
                        by pyrecipe. This class is a factory that returns
                        webscrapers based on the url given. For a list of
                        currently supported sites, look at the scrapers dict.

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""
import uuid
from abc import ABC, abstractmethod

import bs4
import requests


class MalformedUrlError(Exception):
    pass


class SiteNotScrapeable(Exception):
    pass


class WebScraperTemplate(ABC):

    def __init__(self, url, recipe):
        super().__init__()
        req = requests.get(url).text
        self.soup = bs4.BeautifulSoup(req, 'html.parser')
        self.recipe = recipe
        self.recipe.source_url = url

    def scrape(self):
        """Scraper method"""
        self.recipe.name = self.scrape_name()
        self.recipe.prep_time = self.scrape_prep_time()
        self.recipe.cook_time = self.scrape_cook_time()
        self.recipe.author = self.scrape_author()
        self.recipe.ingredients = self.scrape_ingredients()
        self.recipe.steps = self.scrape_method()
        self.recipe.dish_type = 'main'
        return self.recipe

    @abstractmethod
    def scrape_name(self):
        """Scrape the recipe name"""
        pass
    
    @abstractmethod
    def scrape_author(self):
        """Scrape the recipe author."""
        pass
    
    @abstractmethod
    def scrape_prep_time(self):
        """Scrape the prep time"""
        pass

    @abstractmethod
    def scrape_cook_time(self):
        """Scrape the cook time"""
        pass

    @abstractmethod
    def scrape_ingredients(self):
        """Scrape the recipe ingredients."""
        pass

    @abstractmethod
    def scrape_method(self):
        """Scrape the recipe method."""
        pass


class TastyWebScraper(WebScraperTemplate):
    """Web Scraper for https://tasty.co."""

    URL = 'https://tasty.co'

    def scrape_name(self):
        """Recipe name."""
        name_box = self.soup.find('h1', attrs={'class': 'recipe-name'})
        if name_box:
            recipe_name = name_box.text.strip()
        return recipe_name
    
    def scrape_author(self):
        """Recipe author."""
        author = ''
        name_box = self.soup.find('div', attrs={'class': 'byline'})
        if name_box:
            return name_box.text.strip()
        return author
    
    def scrape_prep_time(self):
        """Scrape the recipe name"""
        prep_time = 0
        return prep_time

    def scrape_cook_time(self):
        """Scrape the recipe name"""
        cook_time = 0
        return cook_time

    def scrape_ingredients(self):
        """Recipe ingredients."""
        ingred_box = self.soup.find('ul', attrs={'class': 'list-unstyled xs-text-3'})
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
            recipe_steps.append(item.text.strip())
        return recipe_steps


class AllRecipesWebScraper(WebScraperTemplate):
    """Web Scraper for https://www.allrecipes.com."""

    URL = 'https://www.allrecipes.com'

    def scrape_name(self):
        """Recipe name."""
        name = "headline heading-content elementFont__display"
        name_box = self.soup.find('h1', attrs={'id': 'article-heading_1-0'})
        if name_box:
            return name_box.text.strip()
    
    def scrape_author(self):
        """Recipe author."""
        author = ''
        name = "author-name author-text__block elementFont__detailsLinkOnly--underlined elementFont__details--bold"
        name_box = self.soup.find('a', attrs={'class': name})
        if name_box:
            author = name_box.text.strip()
        return author
    
    def scrape_prep_time(self):
        """Scrape the recipe name"""
        prep_time = 0
        return prep_time

    def scrape_cook_time(self):
        """Scrape the recipe name"""
        cook_time = 0
        return cook_time

    def scrape_ingredients(self):
        """Recipe ingredients."""
        ingred_box = self.soup.find('ul', attrs={'class': 'ingredients-section'})
        ingredients = []
        for litag in ingred_box.find_all('li'):
            ingred = ' '.join(litag.text.strip().split())
            ingredients.append(ingred)
        return ingredients

    def scrape_method(self):
        """Recipe method."""
        method_box = self.soup.find('ul', attrs={'class': 'instructions-section'})
        litags = method_box.find_all('li')
        # Quite often, a recipe site has something unnessasary at the end of
        # the steps such as Enjoy! or 'submit a correction'. be on the look out
        # for such behavior and uncomment the next line if need be.
        #del litags[-1]
        recipe_steps = []
        for item in litags:
            recipe_steps.append(item.text.strip())
        return recipe_steps


scrapers = [eval(s) for s in dir() if s.endswith('Scraper')]

class RecipeWebScraper:
    """Factory for webscrapers."""

    def __init__(self):
        self._scrapers = {}
        self._scrapeable = self._scrapers.keys()
        for item in scrapers:
            self.register_scraper(item)


    def register_scraper(self, scraper):
        self._scrapers[scraper.URL] = scraper

    def scrape(self, url, rec):
        scraper = [s for s in self._scrapeable if url.startswith(s)][0]
        recipe = self._scrapers[scraper](url, rec).scrape()
        return recipe

if __name__ == '__main__':
    pass
