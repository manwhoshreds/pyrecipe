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
import sys
import json
import uuid
import string
from collections import OrderedDict
from zipfile import ZipFile, BadZipFile

from termcolor import colored
from ruamel.yaml import YAML

import pyrecipe.utils as utils
import pyrecipe.config as config
from pyrecipe.db import update_db
from pyrecipe import Q_, CULINARY_UNITS, ureg
from pyrecipe.recipe_numbers import RecipeNum

__all__ = ['Recipe', 'IngredientParser']

# GLOBAL REs
PORTIONED_UNIT_RE = re.compile(r'\(?\d+\.?\d*? (ounce|pound)\)? (cans?|bags?)')
PAREN_RE = re.compile(r'\((.*?)\)')
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
            self.source = utils.get_file_name_from_uuid(self.uuid)

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

    def get_ingredients(self, fmt='object'):
        """
        Get the ingredients and named ingredients at the same time.

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
        for item in self.ingredients:
            if fmt == "string": item = str(item)
            elif fmt == "data": item = item.data
            elif fmt == "quntity": item = item.quantity
            ingreds.append(item)

        named = OrderedDict()
        if self.named_ingredients:
            named_ingreds = self.named_ingredients
            for item in named_ingreds:
                ingred_list = []
                for ingred in named_ingreds[item]:
                    if fmt == "string": ingred = str(ingred)
                    elif fmt == "data": ingred = ingred.data
                    elif fmt == "quntity": ingred = ingred.quantity
                    ingred_list.append(ingred)
                named[item] = ingred_list
        
        return ingreds, named

    @property
    def ingredients(self):
        """Return ingredient data."""
        ingredients = self._recipe_data.get('ingredients', '')
        return [Ingredient(i) for i in ingredients]

    @ingredients.setter
    def ingredients(self, value):
        """Set the ingredients of a recipe.

        Ingredients should be passed in as a list of ingredient strings.
        """
        ingredients = []
        for ingred in value:
            ingred = Ingredient(ingred)
            ingredients.append(ingred.data)

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
                    ingred = Ingredient(ingredient)
                    ingred_list.append(ingred)
                named[named_name] = ingred_list
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
        if data_type in ('json', None):
            sys.exit(json.dumps(self._recipe_data, sort_keys=True,
                                indent=4))
        elif data_type == 'yaml':
            sys.exit(yaml.dump(self._recipe_data, sys.stdout))
        elif data_type == 'xml':
            data = self.get_xml_data()
            sys.exit(data)
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
        string = ''.join(ingred_string).capitalize()
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
        # get note if any
        parens = PAREN_RE.search(string)
        if parens:
            string = string.replace(parens.group(), '').strip()
            self.note = self._strip_parens(parens.group())

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
        self.name = name.strip(',')

if __name__ == '__main__':
    #print(CULINARY_UNITS)
    test = Recipe('korean pork tacos')
    ingreds, named = test.get_ingredients(fmt='string')
    print(ingreds)
    print(named)
