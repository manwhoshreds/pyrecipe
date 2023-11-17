# -*- encoding: UTF-8 -*-
"""
    pyrecipe.recipe
   ~~~~~~~~~~~~~~~
    The recipe module contains the main recipe
    class used to interact with ORF (open recipe format) files.

    - Recipe: The main recipe class is responsible for caching all the
              data associated with an Open Recipe Format file. Give the
              recipe instance an ORF source and all data can be accessed
              like a python dict. You can also assign new attributes or
              change current ones. Use the print_recipe() method to print
              the recipe to standard output and save() to save the data
              back to the same file or one of your own choosing.

              An instance of a recipe class contains all the information
              in a recipe.

              The current recipe data understood by the recipe class can
              be found in the class variable: ORF_KEYS

    - Ingredient: takes a string or a dict of ingredient data

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""
import re
import os
import sys
import json
import string
from typing import List
from copy import deepcopy
from zipfile import ZipFile, BadZipFile
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict

from pyrecipe import utils
from pyrecipe import Quant, CULINARY_UNITS
from pyrecipe.backend.recipe_numbers import RecipeNum


@dataclass
class Recipe:
    """The recipe dataclass"""
    # pylint: disable=too-many-instance-attributes
    recipe_id: int = None
    uuid: str = ''
    name: str = ''
    dish_type: str = ''
    prep_time: int = 0
    cook_time: int = 0
    author: str = ''
    source_url: str = ''
    _ingredients: List[int] = field(default_factory=list)
    steps: List[int] = field(default_factory=list)
    notes: List[int] = field(default_factory=list)

    def _load_file(self, fil):
        '''Load a recipe from a file'''
        try:
            with ZipFile(fil, 'r') as zfile:
                with zfile.open('recipe.json', 'r') as stream:
                    data = json.loads(stream.read())
                    ingreds = data.pop('_ingredients')
                    self._set_data(data)
                    self.ingredients = ingreds
        except BadZipFile as e:
            sys.exit(utils.msg(f"{e}", "ERROR"))

    def _set_data(self, data):
        """Used to set recipe data from incoming dicts such as from webscraper
        and from openrecipes.org
        """
        for key, value in data.items():
            setattr(self, key, value)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __copy__(self):
        cls = self.__class__
        newobj = cls.__new__(cls)
        newobj.__dict__.update(self.__dict__)
        return newobj

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def __eq__(self, other):
        return self.dump_data() == other.dump_data()

    def get_ingredients(self):
        """
        Get the ingredients and named ingredients at the same time.

        This is the recomended way of getting the ingredients for a recipe.
        Example: ingreds, named = recipe.get_ingredients()

        :return: the recipe ingredient and named ingredient objects
        """
        ings = defaultdict(list)
        for ingredient in self.ingredients:
            ings[ingredient.group_name].append(ingredient)
        return dict(ings)

    @staticmethod
    def ingredient(ingredient):
        return Ingredient(ingredient)

    @property
    def ingredients(self):
        """Return ingredient data."""
        return self._ingredients


    @ingredients.setter
    def ingredients(self, value):
        """Set the ingredients of a recipe."""
        #value = ["test"]
        if type(value[0]) in (str, dict):
            for item in value:
                item = Ingredient(item)
                self._ingredients.append(item)
        else:
            self._ingredients = value

    def dump_data(self):
        """Dump a data format to screen.

        This method is mostly useful for troubleshooting
        and development.
        """
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    @property
    def file_name(self):
        return self.uuid.replace('-', '') + '.recipe'

    @property
    def has_id(self):
        return self.recipe_id

    def save_to_file(self, save_to_data_dir=True):
        """save state of class."""
        if save_to_data_dir:
            path = os.path.expanduser('~/.config/pyrecipe/recipe_data')
        else:
            path = os.getcwd()
        data = self.dump_data()
        fil = os.path.join(path, self.file_name)
        with ZipFile(fil, 'w') as zfile:
            zfile.writestr('recipe.json', data)


class Ingredient:
    """Build an Ingredient object.

    :param ingredient: dict or string of ingredient.
    """
    PORTIONED_UNIT_RE = re.compile(r'\(?\d+\.?\d*? (ounce|pound)\)? (cans?|bags?)')
    PAREN_RE = re.compile(r'\((.*?)\)')
    SIZE_STRINGS = ['large', 'medium', 'small', 'heaping']
    PUNCTUATION = ''.join(c for c in string.punctuation if c not in '-/(),.')

    def __init__(self, ingredient):
        self.amount, self.portion, self.size, self.name = ('',) * 4
        self.unit, self.prep, self.note, self.group_name = ('',) * 4
        if isinstance(ingredient, str):
            self.parse_ingredient(ingredient)
        else:
            self.group_name = ingredient.get('group_name', None)
            if self.amount:
                self.amount = RecipeNum(self.amount)
            self.amount = ingredient.get('amount', '')
            self.size = ingredient.get('size', None)
            self.portion = ingredient.get('portion', None)
            self.unit = ingredient.get('unit', None)
            self.name = ingredient['name']
            self.prep = ingredient.get('prep', None)
            self.note = ingredient.get('note', None)


    def __repr__(self):
        return f"<Ingredient('{self.name}')>"


    def __str__(self):
        """Turn ingredient object into a string

        Calling string on an ingredient object returns the gramatically
        correct representation of the ingredient object.
        Though not every ingredients will have all parts, a full ingredient
        string will look like this:

        <amt> <size> <unit>  <name>       <prep>  <note>
        1 heaping tablespoon cumin seeds, toasted (you may use cumin powder)
        """
        ingred_string = []
        if self.unit == 'taste':
            string = "{} to taste".format(self.name.capitalize())
            ingred_string.append(string)
        elif self.unit == 'pinch':
            string = "pinch of {}".format(self.name)
            ingred_string.append(string)
        elif self.unit == 'splash':
            string = "splash of {}".format(self.name)
            ingred_string.append(string)
        else:
            # amnt
            if self.amount:
                ingred_string.append('{}'.format(self.amount))
            # size
            if self.size:
                ingred_string.append(' {}'.format(self.size))
            # portion
            if self.portion:
                ingred_string.append(' ({})'.format(self.portion))
            # unit
            if self.unit:
                if self.unit == 'each':
                    pass
                else:
                    ingred_string.append(' {}'.format(self.unit))

            # name
            ingred_string.append(' {}'.format(self.name))

        if self.prep:
            ingred_string.append(", " + self.prep)
        if self.note:
            note = ' ({})'.format(self.note)
            ingred_string.append(note)
        string = ''.join(ingred_string).strip().capitalize()
        return string

    def _preprocess_string(self, string):
        """preprocess the string"""
        # this special forward slash character (differs from '/') is encounterd
        # on some sites througout the web. There maybe others
        if '⁄' in string:
            string = string.replace('⁄', '/')
        unicode_fractions = {
            '¼': '1/4',
            '½': '1/2',
            '⅓': '1/3',
            '¾': '3/4'
        }
        for frac in unicode_fractions.keys():
            if frac in string:
                string = string.replace(frac, unicode_fractions[frac])

        lower_stripd_punc = self._strip_punct(string).lower()
        return lower_stripd_punc

    def _strip_parens(self, string):
        return ''.join(c for c in string if c not in ('(', ')'))

    def _strip_punct(self, string):
        return ''.join(c for c in string if c not in self.PUNCTUATION)

    @property
    def quantity(self):
        """get the quantity"""
        unit = self.unit
        if not self.unit:
            unit = 'each'
        match = self.PORTIONED_UNIT_RE.search(unit)
        if match:
            unit = match.group().split()
            self.ounce_can = unit[0:2]
            self.amount = 1
            unit = unit[-1]
        return Quant(RecipeNum(self.amount), unit)

    def parse_ingredient(self, string):
        """parse the ingredient string"""
        ingred_string = self._preprocess_string(string)
        # get unit
        match = self.PORTIONED_UNIT_RE.search(ingred_string)
        if match:
            ingred_string = ingred_string.replace(match.group(), '')
            unit = self._strip_parens(match.group()).split()
            self.portion = ' '.join(unit[:2])
            self.unit = unit[-1]
        else:
            if "to taste" in ingred_string:
                self.unit = "taste"
                ingred_string = ingred_string.replace("to taste", '')
            elif "splash of" in ingred_string:
                self.unit = "splash"
                ingred_string = ingred_string.replace("splash of", '')
            elif "pinch of" in ingred_string:
                self.unit = "pinch"
                ingred_string = ingred_string.replace("pinch of", '')
            else:
                for item in CULINARY_UNITS:
                    if item in ingred_string.split():
                        self.unit = item
                        ingred_string = ingred_string.replace(item, '')

        # get note if any
        parens = self.PAREN_RE.search(ingred_string)
        if parens:
            ingred_string = ingred_string.replace(parens.group(), '').strip()
            self.note = self._strip_parens(parens.group())

        ingred_list = ingred_string.split()
        amnt_list = []
        for item in ingred_list:
            try:
                RecipeNum(item)
                amnt_list.append(item)
            except ValueError:
                continue
        try:
            self.amount = str(RecipeNum(' '.join(amnt_list)))
        except ValueError:
            self.amount = None


        ingred_list = [x for x in ingred_list if x not in amnt_list]
        ingred_string = ' '.join(ingred_list)

        for item in self.SIZE_STRINGS:
            if item in ingred_string:
                self.size = item
                ingred_string = ingred_string.replace(item, '')

        for item in CULINARY_UNITS:
            if item in ingred_string.split():
                unit = item
                ingred_string = ingred_string.replace(item, '')

        if ',' in ingred_string:
            self.prep = ingred_string.split(',')[-1].strip()
            ingred_string = ingred_string.replace(self.prep, '')
        else:
            self.prep = None

        if not self.unit:
            self.unit = 'each'

        # at this point we are assuming that all elements have been removed
        name = ' '.join(ingred_string.split())
        self.name = name.strip(', ')


if __name__ == '__main__':
    test = Ingredient('1 3 ounce can onion, chopped')
    print(test.__dict__)
    print(test)
