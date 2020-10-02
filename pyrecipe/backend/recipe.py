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
from collections import OrderedDict
from zipfile import ZipFile, BadZipFile

from termcolor import colored
from ruamel.yaml import YAML

import pyrecipe.utils as utils
from pyrecipe.backend.recipe_numbers import RecipeNum
from pyrecipe import Q_, CULINARY_UNITS

__all__ = ['Recipe']

PORTIONED_UNIT_RE = re.compile(r'\(?\d+\.?\d*? (ounce|pound)\)? (cans?|bags?)')
PAREN_RE = re.compile(r'\((.*?)\)')
HTTP_RE = re.compile(r'^https?\://')
SIZE_STRINGS = ['large', 'medium', 'small', 'heaping']
PUNCTUATION = ''.join(c for c in string.punctuation if c not in '-/(),.')

yaml = YAML(typ='safe')
yaml.default_flow_style = False

class Recipe:
    """Open a recipe file and extract its data for futher processing

    The recipe class can open recipe files and read their data. It can
    change the state of a recipe file and then save the new data back to
    the recipe file.
    """
    # All keys applicable to the Open Recipe Format
    SIMPLE_KEYS = [
        'id', 'uuid', 'name', 'dish_type', 'author', 'category', 'categories', 'tags',
        'description', 'cook_time', 'bake_time', 'notes', 'prep_time', 
        'price', 'recipe_yield', 'region', 'source_book', 'source_url', 'url',
        'steps', 'yields', 'ready_in'
    ]

    # These require their own setters and getters
    COMPLEX_KEYS = [
        'ingredients', '_ingredients', 'named_ingredients',
        '_named_ingredients', 'oven_temp', 'steps'
    ]

    ORF_KEYS = COMPLEX_KEYS + SIMPLE_KEYS
    ALL_KEYS = ORF_KEYS + ['source', '_recipe_data', 'file_name']

    def __init__(self, source=''):
        if isinstance(source, dict):
            self._set_data(source)
        else:
            self.source = source
            self.uuid = str(uuid.uuid4())

    def _set_data(self, data):
        """
        Used to set recipe data from incoming dicts such as from webscraper and
        from openrecipes.org
        """
        for key, value in data.items():
            setattr(self, key, value)
    
    
    def __repr__(self):
        return "<Recipe(name='{}')>".format(self.name)

    
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
        ingreds = self.ingredients

        named = OrderedDict()
        named_ingreds = self.named_ingredients
        for item in self.named_ingredients:
            ingred_list = []
            named_ingred_list = named_ingreds[item]
            ingred_list = named_ingred_list
            named[item] = ingred_list

        return ingreds, named

    @property
    def ingredients(self):
        """Return ingredient data."""
        #ingredients = self.ingredients
        #return [Ingredient(i) for i in ingredients]
        return self._ingredients
        

    @ingredients.setter
    def ingredients(self, value):
        """Set the ingredients of a recipe."""
        if not value:
            return
        if type(value[0]) in (str, dict):
            self._ingredients = [Ingredient(i) for i in value]
        else:
            self._ingredients = [i for i in value]

    @property
    def named_ingredients(self):
        """Return named ingredient data."""
        named = OrderedDict()
        named_ingreds = self._recipe_data.get('named_ingredients', '')
        for item in named_ingreds:
            name = list(item.keys())[0]
            ingred_list = []
            for ingred in list(item.values())[0]:
                ingred = Ingredient(ingred)
                ingred_list.append(ingred)
            named[name] = ingred_list
        return named

    @named_ingredients.setter
    def named_ingredients(self, value):
        """Set named ingredients."""
        if not value:
            return
        named_ingredients = []
        for item in value:
            named_name = list(item.keys())[0]
            ingreds = list(item.values())[0]
            parsed_ingreds = []
            entry = {}
            for ingred in ingreds:
                parsed = Ingredient(ingred)
                parsed_ingreds.append(vars(parsed))
            entry[named_name] = parsed_ingreds
            named_ingredients.append(entry)
        self._named_ingredients = named_ingredients

    @property
    def method(self):
        """Return a list of steps."""
        steps = []
        for step in self.steps:
            steps.append(step['step'])
        return steps

    @method.setter
    def method(self, value):
        value = [{"step": v} for v in value]
        self['steps'] = value

    
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

    @utils.recipe2xml
    def get_xml_data(self):
        """Return the xml data."""
        pass

    def get_json(self):
        data = self._recipe_data
        ingreds, named = self.get_ingredients(fmt="string")
        # just converting ingred data to string so open recipes can
        # process it easily.
        if self.ingredients:
            data['ingredients'] = ingreds
        if self.named_ingredients:
            data['named_ingredients'] = named
        return json.dumps(data, indent=4)

    def dump_data(self, fmt=None):
        """Dump a data format to screen.

        This method is mostly useful for troubleshooting
        and development. It prints data in three formats.
        json, yaml, and xml.

        :param data_type: specify the data type that you wish to dump.
                          'json', 'yaml', 'xml'
        """
        if fmt in ('json', None):
            print(json.dumps(self._recipe_data, indent=4))
        elif fmt == 'yaml':
            yaml.dump(self._recipe_data, sys.stdout)
        elif fmt == 'xml':
            data = self.get_xml_data()
            print(data)
        else:
            raise ValueError('data_type argument must be one of '
                             'json, yaml, or xml')

    def get_yaml_string(self):
        string = io.StringIO()
        yaml.dump(self._recipe_data, string)
        return string.getvalue()

    def save(self):
        """save state of class."""
        stream = io.StringIO()
        yaml.dump(self._recipe_data, stream)
        with ZipFile(self.file_name, 'w') as zfile:
            zfile.writestr('recipe.yaml', stream.getvalue())
            zfile.writestr('MIMETYPE', 'application/recipe+zip')


class Ingredient:
    """Build an Ingredient object.

    :param ingredient: dict or string of ingredient.
    """
    def __init__(self, ingredient):
        self.amount, self.portion, self.size, self.name = ('',) * 4
        self.unit, self.prep, self.note, self.id = ('',) * 4
        if isinstance(ingredient, str):
            self.parse_ingredient(ingredient)
        else:
            self.id = ingredient.get('recipe_ingredient_id', '')
            self.name = ingredient['name']
            self.portion = ingredient.get('portion', '')
            self.size = ingredient.get('size', None)
            self.prep = ingredient.get('prep', '')
            self.note = ingredient.get('note', '')
            self.amount = ingredient.get('amount', '')
            if self.amount:
                self.amount = RecipeNum(self.amount)
            self.unit = ingredient.get('unit', '')


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
        unit = self.unit
        if not self.unit:
            unit = 'each'
        match = PORTIONED_UNIT_RE.search(unit)
        if match:
            unit = match.group().split()
            self.ounce_can = unit[0:2]
            self.amount = 1
            unit = unit[-1]
        return Q_(RecipeNum(self.amount), unit)

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
        return ''.join(c for c in string if c not in PUNCTUATION)

    def parse_ingredient(self, string):
        """parse the ingredient string"""
        # string preprocessing
        ingred_string = self._preprocess_string(string)

        # get unit
        match = PORTIONED_UNIT_RE.search(ingred_string)
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
        parens = PAREN_RE.search(ingred_string)
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

        for item in SIZE_STRINGS:
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
        # from list except for the name. Whatever is left gets joined together
        name = ' '.join(ingred_string.split())
        self.name = name.strip(', ')

if __name__ == '__main__':
    test = Ingredient('1 tablespoon moose hair, roughly chopped')

    test.parse_ingredient('3 teaspoons gandolf hair, complety blown to smitherines')
    r = Recipe()
    r.name = 'stupid'
    print(r)
    print(r.uuid)
