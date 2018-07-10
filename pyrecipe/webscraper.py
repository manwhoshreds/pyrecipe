# -*- encoding: UTF-8 -*-
"""
    pyrecipe.webscraper
    ~~~~~~~~~~~~~~~~~~~
    The recipe webscraper class lets you download recipes from some sites.
    You can either keep the recipe the way it is and just use it with pyrecipe
    or you can use the recipe as a template for your own recpipe development.

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
import sys
import uuid
from abc import ABC, abstractmethod

import bs4
import requests

import pyrecipe.utils as utils


SCRAPERS = {
    'https://tasty.co': 'TastyWebScraper',
    'http://www.geniuskitchen.com': 'GeniusWebScraper',
    'https://www.allrecipes.com': 'AllRecipesWebScraper',
    #'https://www.foodnetwork.com': 'FoodNetworkWebScraper'
}
SCRAPEABLE_SITES = list(SCRAPERS.keys())


class RecipeWebScraper:
    """Factory for webscrapers."""
    
    @staticmethod
    def scrape(url):
        try:
            scrapeable = [s for s in SCRAPEABLE_SITES if url.startswith(s)][0]
        except IndexError:
            # url is not among those listed as scrapeable
            sites = '\n\t'.join(SCRAPEABLE_SITES)
            sys.exit(utils.msg(
                "{} is not scrapeable by pyrecipe. Please select from the "
                "following sites:\n\n\t".format(url), "WARN") +
                utils.msg(sites))

        return eval(SCRAPERS[scrapeable])(url).data


class TemplateWebScraper(ABC):
    
    def __init__(self, url):
        super().__init__()
        self.source_url = url
        req = requests.get(self.source_url).text
        self.soup = bs4.BeautifulSoup(req, 'html.parser')
        self.data = {}
        self.data['uuid'] = str(uuid.uuid4())
        self.__scrape()

    def __scrape(self):
        self.data['prep_time'] = self.scrape_prep_time()
        self.data['cook_time'] = self.scrape_cook_time()
        self.data['name'] = self.scrape_name()
        self.data['author'] = self.scrape_author()
        self.data['ingredients'] = self.scrape_ingredients()
        self.data['named_ingredients'] = self.scrape_named_ingredients()
        self.data['steps'] = self.scrape_method()
        # If site has no dish_type data, default to main
        self.data['dish_type'] = 'main'
    
    @abstractmethod
    def scrape_prep_time(self):
        """Scrape the recipe name"""
        pass
    
    @abstractmethod
    def scrape_cook_time(self):
        """Scrape the recipe name"""
        pass
    
    @abstractmethod
    def scrape_name(self):
        """Scrape the recipe name"""
        pass
        
    @abstractmethod
    def scrape_author(self):
        """Scrape the recipe author."""
        pass

    @abstractmethod
    def scrape_ingredients(self):
        """Scrape the recipe ingredients."""
        pass
    
    @abstractmethod
    def scrape_named_ingredients(self):
        """Scrape the recipe named ingredients."""
        pass
    
    @abstractmethod
    def scrape_method(self):
        """Scrape the recipe method."""
        pass


class GeniusWebScraper(TemplateWebScraper):
    """Web Scraper for http://www.geniuskitchen.com."""
    
    def scrape_prep_time(self):
        """Scrape the recipe name"""
        prep_time = ''
        return prep_time
    
    def scrape_cook_time(self):
        """Scrape the recipe name"""
        cook_time = ''
        return cook_time
    
    def scrape_name(self):
        """Scrape the recipe name."""
        name_box = self.soup.find('h2', attrs={'class': 'modal-title'})
        recipe_name = name_box.text.strip()
        return recipe_name

    def scrape_author(self):
        """Scrape the recipe author."""
        name_box = self.soup.find('h6', attrs={'class': 'byline'})
        recipe_by = name_box.text.strip()
        author = ' '.join(recipe_by.split(' ')[2:]).strip()
        return author

    def scrape_ingredients(self):
        """Scrape the recipe ingredients."""
        attrs = {'class': 'ingredient-list'}
        ingred_box = self.soup.find_all('ul', attrs=attrs)
        ingredients = []
        for item in ingred_box:
            for litag in item.find_all('li'):
                ingred = ' '.join(litag.text.strip().split())
                ingredients.append(ingred)
        return ingredients

    def scrape_named_ingredients(self):
        """Scrape the recipe named ingredients."""
        # Not implemented yet
        named_ingreds = []
        return named_ingreds
    
    def scrape_method(self):
        """Scrape the recipe method."""
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


class TastyWebScraper(TemplateWebScraper):
    """Web Scraper for http://www.tasty.co."""

    def scrape_prep_time(self):
        """Scrape the recipe name"""
        prep_time = ''
        return prep_time
    
    def scrape_cook_time(self):
        """Scrape the recipe name"""
        cook_time = ''
        return cook_time
    
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

    def scrape_named_ingredients(self):
        """Recipe named ingredients."""
        named_ingredients = []
        return named_ingredients
    
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


class AllRecipesWebScraper(TemplateWebScraper):
    """Web Scraper for https://www.allrecipes.com."""
    
    def scrape_prep_time(self):
        """Scrape the recipe name"""
        attrs = {'itemprop': 'prepTime'}
        prep_time = self.soup.find('time', attrs=attrs).get_text()
        prep_time = prep_time.strip(' m')
        return prep_time
    
    def scrape_cook_time(self):
        """Scrape the recipe name"""
        attrs = {'itemprop': 'cookTime'}
        cook_time = self.soup.find('time', attrs=attrs).get_text()
        cook_time = cook_time.strip(' m')
        return cook_time
    
    def scrape_name(self):
        """Scrape the recipe name."""
        attrs = {'class': 'recipe-summary__h1'}
        name_box = self.soup.find('h1', attrs=attrs)
        recipe_name = name_box.text.strip()
        return recipe_name

    def scrape_author(self):
        """Scrape the recipe author."""
        attrs = {'class': 'submitter__name'}
        name_box = self.soup.find('span', attrs=attrs)
        author = name_box.text.strip()
        return author

    def scrape_ingredients(self):
        """Scrape the recipe ingredients."""
        attrs = {'itemprop': 'ingredients'}
        ingred_box = self.soup.find_all('span', attrs=attrs)
        ingredients = []
        for item in ingred_box:
            ingred = ' '.join(item.text.strip().split())
            ingredients.append(ingred)
        return ingredients

    def scrape_named_ingredients(self):
        """Scrape the recipe named ingredients."""
        # Not implemented yet
        named_ingreds = []
        return named_ingreds
    
    def scrape_method(self):
        """Scrape the recipe method."""
        attrs = {'itemprop': 'recipeInstructions'}
        method_box = self.soup.find('ol', attrs=attrs)
        litags = method_box.find_all('li')
        
        recipe_steps = []
        for item in litags:
            step_dict = {}
            step_dict['step'] = item.text.strip()
            recipe_steps.append(step_dict)

        steps = recipe_steps
        return steps


#TODO: FoodNetworkWebScraper IS NOT CURRENTLY WORKING
class FoodNetworkWebScraper(TemplateWebScraper):
    """Web Scraper for https://www.foodnetwork.com."""
    
    def scrape_prep_time(self):
        """Scrape the recipe name"""
        prep_time = ''
        return prep_time
    
    def scrape_cook_time(self):
        """Scrape the recipe name"""
        cook_time = ''
        return cook_time
    
    def scrape_name(self):
        """Recipe name."""
        attrs = {'class': 'o-AssetTitle__a-HeadlineText'}
        name_box = self.soup.find('span', attrs=attrs)
        recipe_name = name_box.text.strip()
        return recipe_name

    def scrape_author(self):
        """Author."""
        attrs = {'class': 'o-Attribution__a-Author'}
        name_box = self.soup.find('div', attrs=attrs)
        author = name_box.find('a').text.strip()
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

    def scrape_named_ingredients(self):
        """Recipe named ingredients."""
        #attrs = {'class': 'o-Ingredients__a-SubHeadline'}
        attrs = {'class': 'o-Ingredients__m-Body'}
        ingred_box = self.soup.find('div', attrs=attrs)
        #TODO: need to make this work if I want to scrape food network
        print(len(list(ingred_box.children)))

            
        exit()
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


if __name__ == '__main__':
    from pyrecipe.recipe import Recipe
    r = Recipe("https://tasty.co/recipe/easy-butter-chicken")
    #r = Recipe("http://www.geniuskitchen.com/recipe/ina-gartens-baked-sweet-potato-fries-333618")
    #r = Recipe("https://www.allrecipes.com/recipe/232062/chef-johns-creme-caramel/")
    #r = Recipe("https://www.foodnetwork.com/recipes/ree-drummond/salisbury-steak-recipe-2126533")
    r.print_recipe()
    #print(r.get_json())
    #test = RecipeWebScraper.get_sites()
