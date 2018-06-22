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

    - Ingredient: Used to parse a dict of ingredient data into a string

    - IngredientParser: Converts an ingredient string into a list or dict
                        of ingredient data elements.

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""
import re
import io
import sys
import uuid
import string
from collections import OrderedDict
from zipfile import ZipFile, BadZipFile

from termcolor import colored
from ruamel.yaml import YAML

import pyrecipe.utils as utils
import pyrecipe.config as config
from pyrecipe.db import update_db
from pyrecipe.recipe_numbers import RecipeNum
from pyrecipe import Q_, ureg

__all__ = ['Recipe', 'IngredientParser']

# GLOBAL REs
PORTIONED_UNIT_RE = re.compile(r'\(?\d+\.?\d*? (ounce|pound)\)? (cans?|bags?)')
PAREN_RE = re.compile(r'\((.*?)\)')

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
        'region',
        'source_book',
        'source_url',
        'steps',
        'tags',
        'uuid',
        'yields'
    ]

    # These have there own setters defined
    COMPLEX_KEYS = [
        'ingredients',
        'named_ingredients',
        'oven_temp',
        'steps'
    ]

    ORF_KEYS = COMPLEX_KEYS + SIMPLE_KEYS

    def __init__(self, source=None, recipe_yield=0):
        if source is not None:
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
            self._recipe_data = {}
            self.dish_type = 'main'
            self.uuid = str(uuid.uuid4())
            #self.yields = [1]
            self.source = utils.get_file_name_from_uuid(self.uuid)

        self.yield_amount = 0
        self.recipe_yield = recipe_yield

    def __repr__(self):
        return "<Recipe(name='{}')>".format(self.name)

    def __dir__(self):
        _dir = ['source']
        return list(self._recipe_data.keys()) + _dir

    def __getattr__(self, key):
        if key in Recipe.ORF_KEYS:
            return self._recipe_data.get(key, '')
        raise AttributeError("'{}' is not an ORF key".format(key))

    def __setattr__(self, key, value):
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

    def get_ingredients(self, yield_amount=0, fmt='string'):
        """Get the ingredients."""
        ingreds = []
        named_ingreds = OrderedDict()
        for item in self.ingredients:
            if fmt == 'string':
                ingreds.append(str(item))
            else:
                ingreds.append(item)
        if self.named_ingredients:
            named_ingreds = self.named_ingredients
            for item in named_ingreds:
                ingred_list = []
                for ingred in named_ingreds[item]:
                    if fmt == "string":
                        ingred_list.append(str(ingred))
                    else:
                        ingred_list.append(ingred)
                named_ingreds[item] = ingred_list
        return ingreds, named_ingreds

    @property
    def ingredients(self):
        """Return ingredient data."""
        ingredients = self._recipe_data.get('ingredients', '')
        return [Ingredient(i, self.yield_amount) for i in ingredients]

    @ingredients.setter
    def ingredients(self, value):
        """Set the ingredients of a recipe.

        Ingredients should be passed in as a list of ingredient strings.
        """
        ingred_parser = IngredientParser()
        ingredients = []
        for item in value:
            ingred = ingred_parser.parse(item)
            ingredients.append(ingred)

        self._recipe_data['ingredients'] = ingredients

    @property
    def named_ingredients(self):
        """Return named ingredient data."""
        named = OrderedDict()
        named_ingreds = self._recipe_data.get('named_ingredients', '')
        if named_ingreds:
            for item in named_ingreds:
                named_name = list(item.keys())[0]
                ingred_list = []
                for ingredient in list(item.values())[0]:
                    ingred = Ingredient(
                        ingredient,
                        yield_amount=self.yield_amount
                    )
                    ingred_list.append(ingred)
                named[named_name] = ingred_list
        return named

    @named_ingredients.setter
    def named_ingredients(self, value):
        """Set named ingredients."""
        ingred_parser = IngredientParser()
        named_ingredients = []
        for item in value:
            named_name = list(item.keys())[0]
            ingreds = list(item.values())[0]
            parsed_ingreds = []
            entry = {}
            for ingred in ingreds:
                parsed = ingred_parser.parse(ingred)
                parsed_ingreds.append(parsed)
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

    @utils.recipe2xml
    def get_xml_data(self):
        """Return the xml data."""
        pass

    def dump_to_screen(self, data_type=None):
        """Dump a data format to screen.

        This method is mostly useful for troubleshooting
        and development. It prints data in three formats.
        raw (just a plain python dictionary with pretty print)
        yaml, and xml.
        """
        if data_type in ('raw', None):
            config.PP.pprint(self._recipe_data)
        elif data_type == 'yaml':
            yaml.dump(self._recipe_data, sys.stdout)
        elif data_type == 'xml':
            print(self.get_xml_data())
        else:
            raise ValueError('data_type argument must be one of '
                             'raw, yaml, or xml')

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

    Given a dict of ingredient data, Ingredient class can return a string
    :param ingredient: dict of ingredient data
    :param yield_amount: choose the yield of the recipe
    :param color: return string with color data for color output
    """
    def __init__(self, ingredient, yield_amount=0):
        self.data = ingredient
        self.name = ingredient['name']
        self.size = ingredient.get('size', '')
        self.prep = ingredient.get('prep', '')
        self.note = ingredient.get('note', '')
        self.link = ingredient.get('link', '')
        self.amounts = ingredient.get('amounts', '')
        try:
            amount = self.amounts[yield_amount].get('amount', '')
            self.amount = RecipeNum(amount)
        except ValueError:
            self.amount = ''
        self.unit = self.amounts[yield_amount]['unit']
        if self.unit == 'each':
            self.unit = ''

    def __repr__(self):
        return "<Ingredient('{}')>".format(self.name)

    def __str__(self):
        """Turn ingredient object into a string

        Calling string on an ingredient object returns the gramatically
        correct representation of the ingredient object.
        """
        if self.note:
            self.note = '({})'.format(self.note)

        if self.unit == 'to taste':
            return "{} to taste".format(self.name.capitalize())
        elif self.unit == 'pinch of':
            return "Pinch of {}".format(self.name)
        elif self.unit == 'splash of':
            return "Splash of {}".format(self.name)
        else:
            match = PORTIONED_UNIT_RE.search(self.unit)
            if match:
                unit = match.group().split()
                self.unit = "({}) {}".format(' '.join(unit[0:2]), unit[-1])
            ingred_string = '{}'.format(self.amount)
            ingred_string += " {} {} {}".format(self.size, self.unit, self.name)
            # the previous line adds unwanted spaces if
            # values are absent, we simply clean that up here.
            ingred_string = " ".join(ingred_string.split())
            if not self.unit and not self.amount:
                ingred_string = "{}".format(self.name.capitalize())
            if self.prep:
                ingred_string += ", " + self.prep
            if self.note:
                ingred_string += " {}".format(self.note)
            return ingred_string

    def get_quantity(self):
        unit = self.unit
        if not self.unit:
            unit = 'each'
        return Q_(self.amount, unit)


class IngredientParser:
    """Convert an ingredient string into a list or dict.

    an excepted ingredient string is usually in the form of

    "<amount> <size> <unit> <ingredient>, <prep>"

    however, not all elements of an ingredient string may
    be present in every case. It is the job of the ingredient
    parser to identify what an ingredient string contains, and to
    return a list or dict populated with the relevant data.

    params:

    - return_dict: return ingredient data in a dict in the form of
                   {'name': <name>,
                    'size': <size>,
                    'amounts': [{'amount': <amount>, 'uniit': <unit>}],
                    'note': <note>,
                    'prep': <prep>}

    examples:

    >>> parser = IngredientParser()
    >>> parser.parse('1 tablespoon onion, chopped')
    [1, '', 'tablespoon', 'onion chopped', 'chopped']
    >>> parser.parse('3 large carrots, finely diced')
    ['3', 'large', 'carrot', 'finely diced']
    >>> parser.parse('1 tablespoon onion chopped', return_dict=True)
    {'amounts': [{'amount': 1, 'unit': 'tablespoon'}], 'name': 'onion chopped', 'prep': 'chopped'}
    """
    def __init__(self):
        omitted = '-/(),.'
        self.punct = ''.join(c for c in string.punctuation if c not in omitted)

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

        lower_stripd_punc = ''.join(c for c in string if c not in self.punct).lower()
        return lower_stripd_punc

    def _strip_parens(self, string):
        return ''.join(c for c in string if c not in ('(', ')'))

    def _strip_punct(self, string):
        #'1 (232323 ounce) can tamatoes, very *&@#finely chopped (I prefer white onions)'
        return ''.join(c for c in string if c not in self.punct)

    def parse(self, string='', return_list=False):
        """parse the ingredient string"""
        amount = ''
        size = ''
        unit = ''
        name = ''
        prep = ''
        note = ''
        ingred_list = []
        ingred_dict = {}

        # string preprocessing
        ingred_string = self._preprocess_string(string)

        # get unit
        match = PORTIONED_UNIT_RE.search(ingred_string)
        if match:
            ingred_string = ingred_string.replace(match.group(), '')
            unit = self._strip_parens(match.group())
        else:
            for item in config.INGRED_UNITS:
                if item in ingred_string.split():
                    unit = item
                    ingred_string = ingred_string.replace(item, '')

        if "to taste" in ingred_string:
            unit = "to taste"
            ingred_string = ingred_string.replace(unit, '')
        elif "splash of" in ingred_string:
            unit = "splash of"
            ingred_string = ingred_string.replace(unit, '')
        elif "pinch of" in ingred_string:
            unit = "pinch of"
            ingred_string = ingred_string.replace(unit, '')

        # get note if any
        parens = PAREN_RE.search(ingred_string)
        if parens:
            ingred_string = ingred_string.replace(parens.group(), '')
            note = self._strip_parens(parens.group())

        ingred_list = ingred_string.split()
        amnt_list = []
        for item in ingred_list:
            try:
                RecipeNum(item)
                amnt_list.append(item)
            except ValueError:
                continue

        try:
            amount = str(RecipeNum(' '.join(amnt_list)))
        except ValueError:
            amount = ''


        ingred_list = [x for x in ingred_list if x not in amnt_list]
        ingred_string = ' '.join(ingred_list)


        for item in config.SIZE_STRINGS:
            if item in ingred_string:
                size = item
                ingred_string = ingred_string.replace(item, '')

        #for item in config.INGRED_UNITS:
        for item in dir(ureg):
            if item in ingred_string.split():
                unit = item
                ingred_string = ingred_string.replace(item, '')

        try:
            assert ',' in ingred_string
            prep = ingred_string.split(',')[-1].strip()
            ingred_string = ingred_string.replace(prep, '')
        except AssertionError:
            prep = ''

        if not unit:
            unit = 'each'

        # at this point we are assuming that all elements have been removed
        # from list except for the name. Whatever is left gets joined together
        name = ' '.join(ingred_string.split())
        name = name.strip(',')
        ingred_dict['amounts'] = [{'amount': amount, 'unit': unit}]
        if size:
            ingred_dict['size'] = size
        ingred_dict['name'] = name
        if prep:
            ingred_dict['prep'] = prep
        if note:
            ingred_dict['note'] = note

        ingred_list = [amount, size, unit, name, prep, note]

        if return_list:
            return ingred_list
        return ingred_dict

if __name__ == '__main__':
    #r = Recipe('')
    print(ureg.get_dimensionality(sys.argv[1]))
    #r.print_recipe()
    #print(r.ingredients)
    #print(r.named_ingredients)
    #print(r.source)
    #r.get_ingredients()
    #print(r._ingredients_cache)
    #print(r._named_ingredients_cache)

