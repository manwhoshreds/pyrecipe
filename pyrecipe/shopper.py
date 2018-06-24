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

import pyrecipe.utils as utils
import pyrecipe.config as config
from pyrecipe import Q_
from pyrecipe.db import dbinfo
from pyrecipe.recipe import Recipe
from pyrecipe.recipe_numbers import RecipeNum

class ShoppingList:
    """Creates a shopping list of ingredients from a list of recipes.

    If duplicate entries are found, ingredients are added together.
    """
    def __init__(self):
        self.recipes = []
        self.ingredients = []
        self.shopping_list = {}

    def _process(self, recipe):
        """Process the ingredients in a recipe."""
        ingreds, named_ingreds = recipe.get_ingredients(fmt='data')
        self._process_ingredients(ingreds)
        if named_ingreds:
            for item in named_ingreds:
                ingreds = named_ingreds[item]
                self._process_ingredients(ingreds)

    def _build_list(self):
        """Build a shopping list from all of the ingredients."""
        for item in self.ingredients:
            name = item.name
            try:
                quant = item.get_quantity()
            except ValueError:
                #print(item)
                #print("errors", item.amount, item.unit)
                continue

            if (name, name + 's') in self.shopping_list.keys():
                orig_ingred = self.shopping_list[name]
                try:
                    addition = orig_ingred + quant
                    self.shopping_list[name] = addition
                except pint.errors.DimensionalityError:
                    self.shopping_list[name] = MultiQuantity(orig_ingred, quant)
            else:
                self.shopping_list[name] = quant

    def print_list(self, write=False):
        """Print the shopping list to stdout."""
        self._build_list()
        print("Recipes:\n")
        for name, dishtype in self.dish_types:
            print("({}) {}".format(dishtype, name))
        print("\n" + utils.S_DIV(45))

        # Print list
        padding = max(len(x) for x in self.shopping_list.keys()) + 1
        for key, value in sorted(self.shopping_list.items()):
            if value.units in ['splash of', 'to taste', 'pinch of']:
                print("{} {}".format(key.ljust(padding, '.'), 'N/A'))
            else:
                try:
                    value.reduce()
                    value = value.round_up()
                except AttributeError:
                    pass
                print("{} {}".format(key.ljust(padding, '.'), str(value)))

    def BAKprint_list(self, write=False):
        """Print the shopping list to stdout."""
        self._build_list()
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
        names = [r.name for r in self.recipes]
        return names

    @property
    def dish_types(self):
        """Get the recipe names."""
        names = self.recipe_names
        dish_types = [r.dish_type for r in self.recipes]
        return zip(names, dish_types)

    def write_to_xml(self):
        """Write the shopping list to an xml file after
           building.
        """
        # Add recipe names to the tree
        for item in self.recipe_names:
            xml_main_dish = etree.SubElement(self.xml_maindish_names, "name")
            xml_main_dish.text = str(item)

        # the salad dressing names
        for item in self.dressing_names:
            xml_dressing_name = etree.SubElement(self.xml_salad_dressing, "name")
            xml_dressing_name.text = str(item)

        # finally, ingreds
        for key, value in self.shopping_list.items():
            try:
                ingred = "{} {}".format(key, str(value.round_up()))
            except AttributeError:
                ingred = "{} {}".format(key, str(value))
            xml_shopping_list_item = etree.SubElement(self.xml_ingredients, "ingredient")
            xml_shopping_list_item.text = str(ingred)

        result = etree.tostring(self.xml_root,
                                xml_declaration=True,
                                encoding='utf-8',
                                with_tail=False,
                                method='xml',
                                pretty_print=True).decode("utf-8")

        print(utils.msg(
            "Writing shopping list to %s"
            % config.SHOPPING_LIST_FILE, 'INFORM'))
        with open(config.SHOPPING_LIST_FILE, "w") as f:
            f.write(result)

    def add_item(self, item, amount):
        """Add a single item to the shopping list."""
        self.shopping_list[item] = amount

    def choose_random(self, count=int(config.RAND_RECIPE_COUNT), write=False):
        try:
            recipe_sample = random.sample(
                dbinfo.get_recipes_by_dishtype('main'),
                count
            )
            rand_salad_dressing = random.choice(
                dbinfo.get_recipes_by_dishtype('salad dressing')
            )
        except ValueError:
            sys.exit(utils.msg(
                "Random count is higher than the amount of recipes"
                " available ({}). Please enter a lower number."
                .format(len(DB.get_data()['main_names'])), "ERROR")
            )
        #self.update(rand_salad_dressing)
        for dish in recipe_sample:
            self.update(dish)
    
    def get_data(self):
        """Convert shoppinglist to json data."""
        data = {}
        data['user_name'] = config.USER_NAME
        data['recipes'] = self.recipe_names
        data['list'] = []
        for name, amount in self.shopping_list.items():
            item = {}
            item['item'], item['amount'] = name, str(amount)
            data['list'].append(item)
        return data
    
    def update(self, source):
        """Update the shopping list with ingredients from source."""
        recipe = Recipe(source)
        self.recipes.append(recipe)
        
        ingreds, named = recipe.get_ingredients(fmt="data")
        for ingred in ingreds:
            self.ingredients.append(ingred)
        for ingred in named:
            self.ingredients += named[ingred]

    def create_new(self):
        """Update openrecipes.org shoppingList."""
        print('updating server...')
        url = 'http://localhost/open_recipes/includes/api/shopping_list/create.php'
        data = self.get_data()
        resp = requests.post(url, json=data)
        print(resp.text)
        #if resp.json()['message'] == 'failed':
        #    print('Something went wrong. The server was not updated')
        #else:
        #    print('Server was updated successfully!')

    def remote(self):
        """Remote."""
        path = 'http://localhost/open_recipes/includes/api/shopping_list/read.php'
        payload = {'user': config.USER_NAME}
        resp = requests.get(path, params=payload)
        print(resp.text)
        #return resp.json()['shopping_list'][0]


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
    shoplist.choose_random()
    shoplist.update('korean pork tacos')
    #shoplist.update('french onion soup')
    #shoplist.update('test')
    #shoplist.update('pesto')
    shoplist.print_list()

