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
import json
import uuid
import shutil
import string
import requests
from collections import OrderedDict
from zipfile import ZipFile, BadZipFile
from copy import copy, deepcopy

from termcolor import colored
from ruamel.yaml import YAML

import pyrecipe.utils as utils
import pyrecipe.config as config
from pyrecipe.db import update_db
from pyrecipe import Q_, CULINARY_UNITS, ureg
from pyrecipe.recipe_numbers import RecipeNum
from pyrecipe.webscraper import RecipeWebScraper

__all__ = ['Recipe', 'IngredientParser']

# GLOBAL REs
PORTIONED_UNIT_RE = re.compile(r'\(?\d+\.?\d*? (ounce|pound)\)? (cans?|bags?)')
PAREN_RE = re.compile(r'\((.*?)\)')
HTTP_RE = re.compile(r'^https?\://')

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
        'author',
        'bake_time',
        'categories',
        'cook_time',
        'description',
        'dish_type',
        'name',
        'notes',
        'prep_time',
        'price',
        'recipe_yield',
        'region',
        'source_book',
        'source_url',
        'steps',
        'tags',
        'uuid',
        'yields'
    ]

    # These require their own setters and getters
    COMPLEX_KEYS = [
        'ingredients',
        'named_ingredients',
        'oven_temp',
        'steps'
    ]

    ORF_KEYS = COMPLEX_KEYS + SIMPLE_KEYS
    ALL_KEYS = ORF_KEYS + ['source', '_recipe_data']

    def __init__(self, source='', recipe_yield=0):
        self._recipe_data = {}
        if isinstance(source, dict):
            self._set_data(source)
        elif HTTP_RE.search(source):
            data = RecipeWebScraper.scrape(source)
            self._set_data(data)
        elif source is not '':
            self.source = utils.get_source_path(source)
            try:
                with ZipFile(self.source, 'r') as zfile:
                    try:
                        with zfile.open('recipe.yaml', 'r') as stream:
                            self._recipe_data = yaml.load(stream)
                    except KeyError:
                        sys.exit(utils.msg("Can not find recipe.yaml. Is this "
                                           "really a recipe file?", "ERROR"))
            except BadZipFile as e:
                sys.exit(utils.msg("{}".format(e), "ERROR"))
        else:
            self.dish_type = 'main'
            self.uuid = str(uuid.uuid4())
            self.source = utils.get_file_name_from_uuid(self.uuid)
        
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        self.recipe_yield = recipe_yield
    
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
        return list(self._recipe_data.keys()) + _dir

    def __getattr__(self, key):
        if key in Recipe.ORF_KEYS:
            return self._recipe_data.get(key, '')
        raise AttributeError("'{}' is not an ORF key or Recipe function"
                             .format(key))

    def __setattr__(self, key, value):
        if key not in self.ALL_KEYS:
            raise AttributeError("Cannot set attribute '{}', its not apart "
                                 "of the ORF spec.".format(key))
        if key in Recipe.SIMPLE_KEYS:
            self._recipe_data[key] = value
        else:
            super().__setattr__(key, value)

    def __delattr__(self, key):
        if key in Recipe.ORF_KEYS:
            try:
                del self._recipe_data[key]
            except KeyError:
                pass
        else:
            del self.__dict__[key]

    __setitem__ = __setattr__
    __getitem__ = __getattr__
    __delitem__ = __delattr__

    def __hash__(self):
        """Get the recipe hash."""
        return hash(self.get_yaml_string())
    
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
        #return self.get_yaml_string() == other.get_yaml_string()
        return self.print_recipe() == other.print_recipe()
    
    @property
    def yields(self):
        """Return a list of recipe yields."""
        return ', '.join(self.yields)

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
        amnt, unit = value.split()
        if len(value.split()) != 2:
            raise RuntimeError("oven_temp format must be '300 F'")
        self._recipe_data['oven_temp'] = {'amount': amnt, 'unit': unit}

    def get_ingredients(self, fmt='object'):
        """
        Get the ingredients and named ingredients at the same time.
        
        This is the recomended way of getting the ingredients for a recipe.
        Example: ingreds, named = recipe.get_ingredients(fmt='string')
        
        :param fmt: specifies the format of the ingredient to be returned.
                    'object', 'string', 'data', 'quantity'
        :type fmt: str
        :return: the recipe ingredients and named ingredients int the format
                 specified
        """
        fmts = ('object', 'string', 'data', 'quantity')
        if fmt not in fmts:
            raise ValueError("fmt should be one of '{}', not '{}'"
                             .format(', '.join(fmts), fmt))

        ingreds = []
        if fmt == "object":
            ingreds = self.ingredients
        elif fmt == "string":
            ingreds = [str(i) for i in self.ingredients]
        elif fmt == "data": 
            ingreds = [i.data for i in self.ingredients]
        elif fmt == "quantity": 
            ingreds = [i.quantity for i in self.ingredients]

        named = OrderedDict()
        named_ingreds = self.named_ingredients
        for item in self.named_ingredients:
            ingred_list = []
            named_ingred_list = named_ingreds[item]
            if fmt == "object": 
                ingred_list = named_ingred_list
            elif fmt == "string":
                ingred_list = [str(i) for i in named_ingred_list]
            elif fmt == "data":
                ingred_list = [i.data for i in named_ingred_list]
            elif fmt == "quantity": 
                ingred_list = [i.quantity for i in named_ingred_list]
            named[item] = ingred_list
        
        return ingreds, named

    @property
    def ingredients(self):
        """Return ingredient data."""
        ingredients = self._recipe_data.get('ingredients', '')
        return [Ingredient(i) for i in ingredients]

    @ingredients.setter
    def ingredients(self, ilist):
        """Set the ingredients of a recipe."""
        ingredients = [Ingredient(i).data for i in ilist]
        self._recipe_data['ingredients'] = ingredients

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
        named_ingredients = []
        for item in value:
            named_name = list(item.keys())[0]
            ingreds = list(item.values())[0]
            parsed_ingreds = []
            entry = {}
            for ingred in ingreds:
                parsed = Ingredient(ingred)
                parsed_ingreds.append(parsed.data)
            entry[named_name] = parsed_ingreds
            named_ingredients.append(entry)
        self._recipe_data['named_ingredients'] = named_ingredients

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

    def print_recipe(self, verbose=False, color=True):
        """Print the recipe to standard output."""
        recipe_str = colored(self.name.title(), 'cyan', attrs=['bold'])
        recipe_str += "\n\nDish Type: {}".format(str(self.dish_type))
        for item in ('prep_time', 'cook_time', 'bake_time'):
            if self[item]:
                recipe_str += "\n{}: {}".format(
                    item.replace('_', ' ').title(),
                    utils.mins_to_hours(RecipeNum(self[item]))
                )

        if self.oven_temp:
            recipe_str += "\nOven temp: {}".format(self.oven_temp)

        if self.author:
            recipe_str += "\nAuthor: {}".format(self.author)

        extra_info = False
        if verbose:
            if self.price:
                recipe_str += "\nPrice: {}".format(self.price)
                extra_info = True
            if self.source_url:
                recipe_str += "\nURL: {}".format(self.source_url)
                extra_info = True
            if self.category:
                recipe_str += ("\nCategory(s): {}"
                               .format(", ".join(self.category)))
                extra_info = True
            if self.yields:
                recipe_str += ("\nYields: " + str(self.yeilds))
                extra_info = True
            if self.notes:
                recipe_str += colored("\n\nNotes:", "cyan")
                wrapped = utils.wrap(self.notes)
                for index, note in wrapped:
                    recipe_str += colored("\n{}".format(index), "yellow")
                    recipe_str += note
                extra_info = True

            if not extra_info:
                recipe_str += '\n'
                recipe_str += utils.msg('No additional information', 'WARN')

        recipe_str += "\n\n{}".format(utils.S_DIV(79))
        recipe_str += colored("\nIngredients:", "cyan", attrs=['underline'])

        # Put together all the ingredients
        ingreds, named_ingreds = self.get_ingredients()
        for ingred in ingreds:
            recipe_str += "\n{}".format(ingred)

        if named_ingreds:
            for item in named_ingreds:
                recipe_str += colored("\n\n{}".format(item.title()), "cyan")

                for ingred in named_ingreds[item]:
                    recipe_str += "\n{}".format(ingred)

        recipe_str += "\n\n{}".format(utils.S_DIV(79))
        recipe_str += colored("\nMethod:", "cyan", attrs=["underline"])

        # print steps
        wrapped = utils.wrap(self.method)
        for index, step in wrapped:
            recipe_str += "\n{}".format(colored(index, "yellow"))
            recipe_str += step

        print(recipe_str)
    
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

    @update_db
    def save(self):
        """save state of class."""
        stream = io.StringIO()
        yaml.dump(self._recipe_data, stream)
        with ZipFile(self.source, 'w') as zfile:
            zfile.writestr('recipe.yaml', stream.getvalue())
            zfile.writestr('MIMETYPE', 'application/recipe+zip')


class Ingredient:
    """Build an Ingredient object.
    
    :param ingredient: dict or string of ingredient.
    """
    def __init__(self, ingredient):
        self.name, self.size, self.prep = ('',) * 3
        self.note, self.amount, self.unit = ('',) * 3
        if isinstance(ingredient, str):
            self.string = ingredient
            self.data = {}
            self._parse_ingredient(ingredient)
            self.data = self.get_data_dict()
        else:
            self.data = ingredient
            self.name = ingredient['name']
            self.size = ingredient.get('size', None)
            self.prep = ingredient.get('prep', '')
            self.note = ingredient.get('note', '')
            self.amount = ingredient.get('amount', '')
            if self.amount:
                self.amount = RecipeNum(self.amount)
            self.unit = ingredient.get('unit')
            self.string = str(self)

    def get_data_dict(self):
        data = {}
        data['name'] = self.name
        if self.size:
            data['size'] = self.size
        if self.prep:
            data['prep'] = self.prep
        if self.note:
            data['note'] = self.note
        data['amount'] = self.amount
        data['unit'] = self.unit
        return data

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
            # unit
            match = PORTIONED_UNIT_RE.search(self.unit)
            if match:
                unit = match.group().split()
                unit = " ({}) {}".format(' '.join(unit[0:2]), unit[-1])
                ingred_string.append(unit)
            elif self.unit == 'each':
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

    def _parse_ingredient(self, string):
        """parse the ingredient string"""
        # string preprocessing
        ingred_string = self._preprocess_string(string)

        # get unit
        match = PORTIONED_UNIT_RE.search(ingred_string)
        if match:
            ingred_string = ingred_string.replace(match.group(), '')
            self.unit = self._strip_parens(match.group())
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

        for item in config.SIZE_STRINGS:
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
    url = "http://localhost/open_recipes/includes/api/recipe/search.php"
    resp = requests.get(url, params={'s': sys.argv[1]})
    res = resp.json()['recipes']
    for item in res:
        print(item['name'])
