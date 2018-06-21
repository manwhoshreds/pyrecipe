"""
    pyrecipe.shopper
    ~~~~~~~~~~~~~~~~
    The shopper module allows you to build a shopping list of ingredients
    from your recipes.

    - ShoppingList: The main shopper class 

    - RandomShoppingList: A ShoppingList subclass that chooses recipes at 
                          random an builds a shopping list.

    - MultiQuantity: A pint Quantity container that holds Quantities of
                     differing dimensionalities because they cannot be added
                     together.

"""
import os
import sys
import json
import random
import datetime

import requests
import pint.errors

import pyrecipe.db as DB
import pyrecipe.utils as utils
import pyrecipe.config as config
from pyrecipe import Q_
from pyrecipe.recipe import Recipe
from pyrecipe.recipe_numbers import RecipeNum

class ShoppingList:
    """Creates a shopping list of ingredients from a list of recipes.

    If duplicate entries are found, ingredients are added together.
    """
    def __init__(self):
        self.recipes = []
        self.shopping_list = {}

    def _process(self, recipe):
        """Process the ingredients in a recipe."""
        ingredients = recipe.ingredients
        alt_ingredients = recipe.alt_ingredients
        self._process_ingredients(ingredients)
        if alt_ingredients:
            for item in alt_ingredients:
                ingreds = list(item.values())[0]
                self._process_ingredients(ingreds)

    def _process_ingredients(self, ingredients):
        """Process ingredients."""
        for item in ingredients:
            item = item.data
            name = item['name']
            try:
                # links are recipe ingredients that are also 
                # recipes so we add it to the list here.
                link = item['link']
                self.update(link)
                if link:
                    continue
            except KeyError:
                pass

            if name == "s&p":
                continue
            try:
                amount = RecipeNum(item['amounts'][0].get('amount', 0))
            except ValueError:
                amount = 0
            unit = item['amounts'][0].get('unit', '')
            if unit in ['splash of', 'to taste', 'pinch of']:
                continue

            # FIXME:
            # pint cannot handle units such as '16 ounce can' etc....
            # this is a workaround until a better solution is found
            if 'can' in unit:
                unit = 'can'
            try:
                quant = Q_(amount, unit)
            except ValueError:
                print("errors", amount, unit)
                continue

            if name in self.shopping_list.keys():
                orig_ingred = self.shopping_list[name]
                try:
                    addition = orig_ingred + quant
                    self.shopping_list[name] = addition
                except pint.errors.DimensionalityError:
                    self.shopping_list[name] = MultiQuantity(orig_ingred, quant)
            else:
                self.shopping_list[name] = quant

    def BAKprint_list(self, write=False):
        """Print the shopping list to stdout."""
        print("Recipes:\n")
        for name, dishtype in self.dish_types:
            print("({}) {}".format(dishtype, name))
        print("\n" + utils.S_DIV(45))

        # Print list
        padding = max(len(x) for x in self.shopping_list.keys()) + 1
        for key, value in self.shopping_list.items():
            if value.units in ['splash of', 'to taste', 'pinch of']:
                print("{} {}".format(key.ljust(padding, '.'), 'N/A'))
            else:
                try:
                    #value = value.round_up().reduce()
                    #value = value.reduce()
                    print("{} {}".format(key.ljust(padding, '.'), str(value)))
                except AttributeError:
                    print("{} {}".format(key.ljust(padding, '.'), value))

    def print_list(self, write=False):
        """Print the shopping list to stdout."""
        print("Recipes:\n")
        for name, dishtype in self.dish_types:
            print("({}) {}".format(dishtype, name))
        print("\n" + utils.S_DIV(45))

        # Print list	
        padding = max(len(x) for x in self.remote().keys()) + 1
        for key, value in self.remote().items():
            try:
                #value = value.round_up().reduce()
                #value = value.reduce()
                print("{} {}".format(key.ljust(padding, '.'), str(value)))
            except AttributeError:
                print("{} {}".format(key.ljust(padding, '.'), value))
    
    @property
    def recipe_names(self):
        """Get the recipe names."""
        names = [r.recipe_name for r in self.recipes]
        return names

    @property
    def dish_types(self):
        """Get the recipe names."""
        names = [r.recipe_name for r in self.recipes]
        dish_types = [r['dish_type'] for r in self.recipes]
        return zip(names, dish_types)
    
    def add_item(self, item, amount):
        """Add a single item to the shopping list."""
        self.shopping_list[item] = amount

    def choose_random(self, count=int(config.RAND_RECIPE_COUNT), write=False):
        try:
            recipe_sample = random.sample(DB.get_data()['main_names'], count)
            rand_salad_dressing = random.choice(DB.get_data()['salad_dressing_names'])
        except ValueError:
            sys.exit(utils.msg(
                "Random count is higher than the amount of recipes"
                " available ({}). Please enter a lower number."
                .format(len(DB.get_data()['main_names'])), "ERROR"
            ))
        self.update(rand_salad_dressing)
        for dish in recipe_sample:
            self.update(dish)
    
    def to_json(self):
        """Convert shoppinglist to json data."""
        data = {}
        data['user_name'] = config.USER_NAME
        data['recipes'] = self.recipe_names
        data['list'] = []
        for name, amount in self.shopping_list.items():
            item = {}
            item['item'], item['amount'] = name, str(amount)
            data['list'].append(item)
        #return json.dumps(data)
        return data
    
    def update(self, source):
        """Update the shopping list with ingredients from source."""
        try:
            recipe = Recipe(source)
        except utils.RecipeNotFound:
            print("{} not found in database. Skipping...".format(source))
            return
        self.recipes.append(recipe)
        self._process(recipe)

    def update_remote(self):
        """Update openrecipes.org shoppingList."""
        #path = 'http://localhost/open_recipes/includes/api/shopping_list/create.php'
        path = 'http://192.168.0.31/openRecipes/includes/api/shopping_list/create.php'
        data = self.to_json()
        resp = requests.post(path, json=data)
        print(resp.reason)
        print(resp.text)

    def remote(self):
        path = 'http://localhost/open_recipes/includes/api/shopping_list/read.php'
        payload = {'user': config.USER_NAME}
        resp = requests.get(path, params=payload)
        return resp.json()['shopping_list'][0]



class MultiQuantity:
    """Class to deal with quantities of different dimentions"""

    def __init__(self, *args):
        self.quants = []
        self.type_test = type(Q_('1', 'teaspoon'))
        for item in args:
            if not isinstance(item, self.type_test):
                raise TypeError('arguments must be of type Quantity, '
                                'not ' + str(item))
            else:
                self.quants.append(item)

    def __str__(self):
        test = [str(x) for x in self.quants]
        return ' + '.join(test)

    def __repr__(self):
        return '<MultiQuantity({})>'.format(self.quants)

    def __add__(self, other):
        if not isinstance(other, self.type_test):
            raise TypeError('Quantity types can only be added to MultiQuantity')
        for item in self.quants:
            try:
                addition = item + other
                self.quants.remove(item)
                self.quants.append(addition)
                break
            except pint.errors.DimensionalityError:
                continue
        return self

    @property
    def units(self):
        return 'n/a'

if __name__ == '__main__':
    shoplist = ShoppingList()
    #shoplist.update('korean pork tacos')
    #shoplist.update('french onion soup')
    #shoplist.update('test')
    #shoplist.update('pesto')
    #shoplist.update('carrot cake')
    #shoplist.update_remote()
    #shoplist.read_from_remote()
    #shoplist.update_remote()
    shoplist.print_list()

