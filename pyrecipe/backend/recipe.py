# -*- encoding: UTF-8 -*-
"""
    pyrecipe.recipe
   ~~~~~~~~~~~~~~~
    The recipe module contains the main recipe
    class used to interact with ORF (open recipe format) files.
    You can simply print the recipe or print the xml dump.

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
import io
import os
import sys
import uuid
import json
import shutil
import string
from copy import deepcopy
from typing import List
from zipfile import ZipFile, BadZipFile
from dataclasses import dataclass, field
from itertools import zip_longest
from collections import OrderedDict
from collections import defaultdict

from ruamel.yaml import YAML

import pyrecipe.utils as utils
from pyrecipe import Quant, CULINARY_UNITS
from pyrecipe.backend.recipe_numbers import RecipeNum
from pyrecipe.backend.database import RecipeDB
#from pyrecipe.backend.webscraper import MalformedUrlError, SiteNotScrapeable


yaml = YAML(typ='safe')
yaml.default_flow_style = False


@dataclass
class RecipeData:
    """The recipe dataclass"""
    id: int = None
    uuid: str = None
    name: str = None
    dish_type: str = None
    author: str = None
    _ingredients: List[int] = field(default_factory=list)
    #_named_ingredients: OrderedDict()


    # All keys applicable to the Open Recipe Format
    SIMPLE_KEYS = [
        'id', 'uuid', 'name', 'dish_type', 'author', 'category', 'categories', 
        'tags', 'description', 'cook_time', 'bake_time', 'prep_time', 
        'ready_in', 'notes', 'price', 'yield', 'yields', 'region', 
        'sourcebook', 'steps', 'url', 'source_url', 'recipe_yield'
    ]

    # These require their own setters and getters
    COMPLEX_KEYS = [
        'ingredients', '_ingredients', 'named_ingredients',
        '_named_ingredients', 'oven_temp', 'steps', 'set_method'
    ]

    ORF_KEYS = COMPLEX_KEYS + SIMPLE_KEYS
    ALL_KEYS = ORF_KEYS + ['source', '_recipe_data', 'file_name']

    def ___init__(self, source=''):
        self._ingredients = []
        if isinstance(source, dict):
            self._set_data(source)
            return
        
        if os.path.isfile(source):
            self._load_file(source)
            return
        
        if isinstance(source, str):
            self.uuid = str(uuid.uuid4())
            self.name = source
            return
        #try:
        #    return scraper.scrape(source)
        #except MalformedUrlError:
        #    pass
        #except SiteNotScrapeable as e:
        #    return e
    
    
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
            sys.exit(utils.msg("{}".format(e), "ERROR"))
    

    def _set_data(self, data):
        """Used to set recipe data from incoming dicts such as from webscraper 
        and from openrecipes.org
        """
        for key, value in data.items():
            setattr(self, key, value)

    def __hash__(self):
        return 3
    
    def __dir__(self):
        _dir = ['source']
        return list(self.__dict__.keys()) + _dir

    def __getattr__(self, key):
        if key in Recipe.ALL_KEYS:
            return self.__dict__.get(key, '')
        raise AttributeError("'{}' is not an ORF key or Recipe function"
                             .format(key))
    
    def __setattr__(self, key, value):
        if key not in self.ALL_KEYS:
            raise AttributeError("Cannot set attribute '{}', its not apart "
                                 "of the ORF spec.".format(key))
        if key in Recipe.SIMPLE_KEYS:
            self.__dict__[key] = value
        else:
            super().__setattr__(key, value)

    def __delattr__(self, key):
        if key in Recipe.ORF_KEYS:
            try:
                del self.__dict__[key]
            except KeyError:
                pass

    __setitem__ = __setattr__
    __getitem__ = __getattr__
    __delitem__ = __delattr__

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
        return self.get_yaml_string() == other.get_yaml_string()

    @property
    def oven_temp(self):
        """Return the oven temperature string."""
        temp = self._recipe_data.get('oven_temp', '')
        if temp:
            temp = "{} {}".format(temp['amount'], temp['unit'])
        return temp

    @oven_temp.setter
    def oven_temp(self, value):
        """Set the oven temperature."""
        return
        amnt, unit = value.split()
        if len(value.split()) != 2:
            raise RuntimeError("oven_temp format must be '300 F'")
        self._recipe_data['oven_temp'] = {'amount': amnt, 'unit': unit}

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
        if type(value[0]) in (str, dict):
            for item in value:
                item = Ingredient(item)
                self._ingredients.append(item)
        else:
            self._ingredients = value

    def add_ingredient(self, ingredient, group):
        ingred = Ingredient(ingredient, group=group)
        self._ingredients.append(ingred)
    
    @property
    def named_ingredients(self):
        """Return named ingredient data."""
        return self._ingredients

    @named_ingredients.setter
    def named_ingredients(self, value):
        """Set named ingredients."""
        named = OrderedDict()
        for item in value:
            name = list(item.keys())[0]
            ingred_list = []
            for ingred in list(item.values())[0]:
                if type(ingred) in (str, dict):
                    ingred['group_name'] = name
                    ingred = Ingredient(ingred)
                self._ingredients.append(ingred)

    def export(self, fmt, path):
        """Export the recipe in a chosen file format."""
        fmts = ('xml', 'recipe')
        if fmt not in fmts:
            raise ValueError('Format must be one of {}'.format(' '.join(fmts)))

        file_name = utils.get_file_name_from_recipe(self.name, fmt)
        file_name = os.path.join(path, file_name)

        if fmt == 'xml':
            print(utils.msg("Writing to file: {}".format(file_name), "INFORM"))
            with open(file_name, "w") as file:
                file.write(str(xml))

        elif fmt == 'recipe':
            src = self.source
            dst = os.path.join(path, file_name)
            if os.path.isfile(dst):
                sys.exit(utils.msg("File already exists.", "ERROR"))
            else:
                shutil.copyfile(src, dst)

    def get_json(self):
        """get json from recipe"""
        data = self._recipe_data
        ingreds, named = self.get_ingredients(fmt="string")
        # just converting ingred data to string so open recipes can
        # process it easily.
        if self.ingredients:
            data['ingredients'] = ingreds
        if self.named_ingredients:
            data['named_ingredients'] = named
        return json.dumps(data, indent=4)

    def dump_data(self, fmt='json'):
        """Dump a data format to screen.

        This method is mostly useful for troubleshooting
        and development. It prints data in three formats.
        json, yaml, and xml.

        :param data_type: specify the data type that you wish to dump.
                          'json', 'yaml', 'xml'
        """
        if fmt == 'json':
            print(json.dumps(self, default=lambda o: o.__dict__, indent=4))
        elif fmt == 'yaml':
            yaml.dump(self._recipe_data, sys.stdout)
        elif fmt == 'xml':
            data = self.get_xml_data()
            print(data)
        else:
            raise ValueError('data_type argument must be one of '
                             'json, yaml, or xml')

    def get_yaml_string(self):
        """get the yaml string"""
        string = io.StringIO()
        yaml.dump(self.__dict__, string)
        return string.getvalue()
    
    @property
    def file_name(self):
        return self.uuid.replace('-', '') + '.recipe'
    
    def save_to_file(self, save_to_data_dir=True):
        """save state of class."""
        if save_to_data_dir:
            path = os.path.expanduser('~/.config/pyrecipe/recipe_data')
        else: 
            path = os.getcwd()
        data = json.dumps(self, default=lambda o: o.__dict__, indent=4)
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
    ggroup_name = None
    
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
        return "<Ingredient('{}')>".format(self.name)


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

    def _preprocess_string(self, string):
        """preprocess the string"""
        # this special forward slash character (differs from '/') is encounterd
        # on some sites througout the web. There maybe others
        if '⁄' in string:
            string = string.replace('⁄', '/')
        unicode_fractions = {
            '¼': '1/4',
            '½': '1/2',
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
            self.amount = ''


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
            self.prep = ''

        if not self.unit:
            self.unit = 'each'

        # at this point we are assuming that all elements have been removed
        name = ' '.join(ingred_string.split())
        self.name = name.strip(', ')


class Recipe(RecipeData):
    """Recipe Factory""" 

    def __init__(self, source):
        super().__init__()
        
        if isinstance(source, dict):
            self._set_data(source)
            return
        
        if os.path.isfile(source):
            self._load_file(source)
            return
        
        if isinstance(source, str):
            self.name = source
            db = RecipeDB()
            test = db.read_recipe(self)
            #print(test.__dict__)
            #self.uuid = str(uuid.uuid4())
            #self.name = source
            return
        #try:
        #    return scraper.scrape(source)
        #except MalformedUrlError:
        #    pass
        #except SiteNotScrapeable as e:
        #    return e

    def __repr__(self):
        return "<Recipe(name='{}')>".format(self.name)

if __name__ == '__main__':
    db = RecipeDB()
    for item in db.recipes:
        r = Recipe(item)
        r.save_to_file(save_to_data_dir=True)
    
