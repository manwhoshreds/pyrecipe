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
import sys
import uuid
from abc import ABC, abstractmethod

import bs4
import requests

import pyrecipe.utils as utils
from pyrecipe.recipe import Recipe


SCRAPERS = {
    #'https://www.food.com': 'FoodWebScraper',
    'https://tasty.co': 'TastyWebScraper',
    'https://www.bigoven.com': 'BigOvenWebScraper',
    #'https://www.allrecipes.com': 'AllRecipesWebScraper',
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
                "following sites:\n\n{}".format(url, sites), "WARN"))

        return eval(SCRAPERS[scrapeable])(url).recipe


class TemplateWebScraper(ABC):
    
    def __init__(self, url):
        super().__init__()
        req = requests.get(url).text
        self.soup = bs4.BeautifulSoup(req, 'html.parser')
        self.recipe = Recipe()
        self.recipe.uuid = str(uuid.uuid4())
        self.recipe.source_url = url
        self.__scrape()

    def __scrape(self):
        self.recipe.prep_time = self.scrape_prep_time()
        self.recipe.cook_time = self.scrape_cook_time()
        self.recipe.name = self.scrape_name()
        self.recipe.author = self.scrape_author()
        self.recipe.ingredients = self.scrape_ingredients()
        self.recipe.named_ingredients = self.scrape_named_ingredients()
        self.recipe.steps = self.scrape_method()
        self.recipe.dish_type = 'main'
    
    @abstractmethod
    def scrape_prep_time(self):
        """Scrape the prep time"""
        pass
    
    @abstractmethod
    def scrape_cook_time(self):
        """Scrape the cook time"""
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


class FoodWebScraper(TemplateWebScraper):
    """Web Scraper for https://www.food.com."""
    
    def scrape_prep_time(self):
        """Scrape the prep time"""
        prep_time = ''
        return prep_time
    
    def scrape_cook_time(self):
        """Scrape the cook time"""
        cook_time = ''
        return cook_time
    
    def scrape_name(self):
        """Scrape the recipe name."""
        name_box = self.soup.find('div', attrs={'class': 'recipe-title'})
        recipe_name = name_box.text.strip()
        return recipe_name

    def scrape_author(self):
        """Scrape the recipe author."""
        name_box = self.soup.find('a', attrs={'class': 'recipe-details__author-link theme-color'})
        author = name_box.text.strip()
        return author

    def scrape_ingredients(self):
        """Scrape the recipe ingredients."""
        attrs = {'class': 'recipe-ingredients__ingredient-part'}
        ingred_box = self.soup.find_all('span', attrs=attrs)
        print(ingred_box)
        ingredients = []
        for item in ingred_box:
            for litag in item.find_all('li'):
                ingred = ' '.join(litag.text.strip().split())
                ingredients.append(ingred)
        print(ingredients)
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


class BigOvenWebScraper(TemplateWebScraper):
    """Web Scraper for https://www.bigoven.com."""

    def scrape_prep_time(self):
        """Scrape the prep time"""
        prep_time = ''
        return prep_time
    
    def scrape_cook_time(self):
        """Scrape the cook time"""
        cook_time = ''
        return cook_time
    
    def scrape_name(self):
        """Scrape the recipe name."""
        attributes = {'class', 'recipe-container modern'}
        name_box = self.soup.find('div', attrs=attributes)
        name_box = name_box.find('h1')
        recipe_name = name_box.text.strip()
        return recipe_name

    def scrape_author(self):
        """Scrape the recipe author."""
        return "No author"

    def scrape_ingredients(self):
        """Scrape the recipe ingredients."""
        attrs = {'class': 'recipe-ingredients__ingredient-part'}
        ingred_box = self.soup.find_all('span', attrs=attrs)
        print(ingred_box)
        ingredients = []
        for item in ingred_box:
            for litag in item.find_all('li'):
                ingred = ' '.join(litag.text.strip().split())
                ingredients.append(ingred)
        print(ingredients)
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
        attrs = {'class': 'recipe-title'}
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
        attrs = {'itemprop': 'recipeIngredient'}
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
    webrecipe = "https://tasty.co/recipe/easy-butter-chicken"
    #webrecipe = "http://www.geniuskitchen.com/recipe/ina-gartens-baked-sweet-potato-fries-333618"
    #webrecipe = "https://www.allrecipes.com/recipe/232062/chef-johns-creme-caramel/"
    #webrecipe = "https://www.foodnetwork.com/recipes/ree-drummond/salisbury-steak-recipe-2126533"
    #webrecipe = "https://www.food.com/recipe/easiest-greek-salad-dressing-428819"
    r = RecipeWebScraper.scrape(webrecipe)
    r.print_recipe()
    #print(r.get_json())
    #test = RecipeWebScraper.get_sites()
