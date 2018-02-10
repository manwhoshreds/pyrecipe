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
              the recipe to standard output and dump() to save the data
              back to the same file or one of your own choosing.

              An instance of a recipe class contains all the information
              in a recipe.

              The current recipe data understood by the recipe class can
              be found in the class variable: orf_keys


    - RecipeWebScraper: The pyrecipe web_scraper class is a web
                        scraping utility used to download and analyze
                        recipes found on websites in an attempt to
                        save the recipe data in the format understood
                        by pyrecipe.
                        Currently supported sites: www.geniuskitchen.com
    * Inherits from Recipe

    - Ingredient: Returns a gramatically correct ingredient string given
                  the elments of ingredient data

    - IngredientParser: Converts an ingredient string into a list or dict
                        of ingredient data elements.

    copyright: 2017 by Michael Miller
    license: GPL, see LICENSE for more details.
"""

import sys
import os
import re
import io
import textwrap
from fractions import Fraction
from zipfile import ZipFile, BadZipFile
from numbers import Number
from lxml import etree
from urllib.request import urlopen

import bs4
import yaml
from pyrecipe import ureg, Q_, p, color, RecipeNum #yaml
from pyrecipe.config import (S_DIV, RECIPE_DATA_FILES,
                             SCRIPT_DIR, PP, CAN_UNITS,
                             INGRED_UNITS, SIZE_STRINGS,
                             PREP_TYPES, RECIPE_DATA_DIR)
from pyrecipe.utils import check_source, get_file_name, mins_to_hours, all_singular


class Recipe:
    """The recipe class is used to perform operations on
    recipe source files such as print and save xml.
    """
    # All keys applicable to the Open Recipe Format
    orf_keys = ['recipe_name', 'recipe_uuid', 'dish_type',
                'category',    'cook_time',   'prep_time',
                'author',      'oven_temp',   'bake_time',
                'yields',      'ingredients', 'alt_ingredients',
                'notes',       'source_url',  'steps',
                'tags',        'source_book', 'price']

    def __init__(self, source=''):
        self.source = source
        self.xml_root = etree.Element('recipe')
        if self.source:
            self.source = check_source(source)
            try:
                with ZipFile(self.source, 'r') as zfile:
                    try: 
                        with zfile.open('recipe.yaml', 'r') as stream:
                            self._recipe_data = yaml.load(stream)
                    except KeyError:
                        sys.exit("{}ERROR: Can not find recipe.yaml."
                                 " Is this really a recipe file?"
                                 .format(color.ERROR, self.source))
            except BadZipFile:
                    sys.exit("{}ERROR: This file is not a zipfile."
                             .format(color.ERROR, self.source))

        else:
            self._recipe_data = {}
            # dish type should default to main
            self['dish_type'] = 'main'

        # All root keys included in the particular source which may
        # or may not include all keys from the orf spec
        self.yaml_root_keys = list(self._recipe_data.keys())

        # alt_ingreds
        self._has_alt_ingreds = False
        if self['alt_ingredients']:
            self._has_alt_ingreds = True
            self.alt_ingreds = []
            # building a list of alternative ingredient names here helps later
            # in get_ingredients()
            for item in self['alt_ingredients']:
                name = list(item.keys())
                self.alt_ingreds += name
        
        # Scan the recipe to build the xml
        self._scan_recipe()
    
    def _scan_recipe(self):
        """Internal method used to build the xml tree"""
        # recipe name
        if self['recipe_name']:
            xml_recipe_name = etree.SubElement(self.xml_root, "name")
            xml_recipe_name.text = self['recipe_name']

        # recipe_uuid
        if self['recipe_uuid']:
            xml_recipe_uuid = etree.SubElement(self.xml_root, "uuid")
            xml_recipe_uuid.text = str(self['recipe_uuid'])

        # dish_type
        if self['dish_type']:
            xml_dish_type = etree.SubElement(self.xml_root, "dish_type")
            xml_dish_type.text = self['dish_type']

        # category
        if self['category']:
            for entry in self['category']:
                xml_category = etree.SubElement(self.xml_root, "category")
                xml_category.text = str(entry)

        # author
        if self['author']:
            xml_author = etree.SubElement(self.xml_root, "author")
            xml_author.text = self['author']

        # prep_time
        if self['prep_time']:
            xml_prep_time = etree.SubElement(self.xml_root, "prep_time")
            xml_prep_time.text = str(self['prep_time'])

        # cook_time
        if self['cook_time']:
            xml_cook_time = etree.SubElement(self.xml_root, "cook_time")
            xml_cook_time.text = str(self['cook_time'])

        # bake_time
        if self['bake_time']:
            xml_bake_time = etree.SubElement(self.xml_root, "bake_time")
            xml_bake_time.text = str(self['bake_time'])

        # ready_in
        # not actually an ord tag, so is not read from recipe file
        # it is simply calculated within the class
        if self['prep_time'] and self['cook_time']:
            self['ready_in'] = RecipeNum(self['prep_time']) + RecipeNum(self['cook_time'])
        elif self['prep_time'] and self['bake_time']:
            self['ready_in'] = RecipeNum(self['prep_time']) + RecipeNum(self['bake_time'])
        else:
            self['ready_in'] = self['prep_time']

        # notes
        if self['notes']:
            pass

        # price
        if self['price']:
            xml_price = etree.SubElement(self.xml_root, "price")
            xml_price.text = str(self['price'])

        # oven_temp
        if self['oven_temp']:
            self.oven_temp = self['oven_temp']
            self.ot_amount = self['oven_temp']['amount']
            self.ot_unit = self['oven_temp']['unit']
            xml_oven_temp = etree.SubElement(self.xml_root, "oven_temp")
            xml_oven_temp.text = str(self.ot_amount) + " " + str(self.ot_unit)

        # yields
        if self['yields']:
            xml_yields = etree.SubElement(self.xml_root, "yields")
            for yeld in self['yields']:
                xml_servings = etree.SubElement(xml_yields, "servings")
                xml_servings.text = str(yeld)

        # ingredients
        if self['ingredients']:
            xml_ingredients = etree.SubElement(self.xml_root, "ingredients")
            for ingred in self.get_ingredients():
                xml_ingred = etree.SubElement(xml_ingredients, "ingred")
                xml_ingred.text = ingred

        # alt_ingredients
        try:
            for item in self.alt_ingreds:
                xml_alt_ingredients = etree.SubElement(self.xml_root,
                                                       "alt_ingredients")
                xml_alt_ingredients.set('alt_name', item.title())
                for ingred in self.get_ingredients(alt_ingred=item):
                    xml_alt_ingred = etree.SubElement(xml_alt_ingredients,
                                                      "alt_ingred")
                    xml_alt_ingred.text = ingred
        except (AttributeError, TypeError):
                pass
        # steps
        xml_steps = etree.SubElement(self.xml_root, "steps")
        for step in self['steps']:
            steps_of = etree.SubElement(xml_steps, "step")
            steps_of.text = step['step']
    
    def __str__(self):
        """Returns the complete string representation of the recipe data."""
        recipe_string = ''
        recipe_string += self['recipe_name'].title() + "\n"
        recipe_string += "\nIngredients:\n"

        # Put together all the ingredients
        for ingred in self.get_ingredients():
            recipe_string += "{}\n".format(ingred)
        try:
            for item in self.alt_ingreds:
                recipe_string += "\n{}\n".format(item.title())
                for ingred in self.get_ingredients(alt_ingred=item):
                    recipe_string += "{}\n".format(ingred)
        except AttributeError:
                pass

        recipe_string += "\nMethod:\n"
        # print steps
        for index, step in enumerate(self['steps'], start=1):
            recipe_string += "{}. {}\n".format(index, step['step'])
        return recipe_string

    def __repr__(self):
        return "<pyrecipe.recipe.Recipe name='{}'>"\
                .format(self['recipe_name'])

    def __getitem__(self, key):
        if key in __class__.orf_keys:
            return self.__dict__['_recipe_data'].get(key, '')
        else:
            return self.__dict__.get(key, '')

    def __setitem__(self, key, value):
        if key == 'recipe_name':
            self.source = get_file_name(value)
        if key in __class__.orf_keys:
            self.__dict__['_recipe_data'][key] = value
            self._scan_recipe()
        else:
            self.__dict__[key] = value

    def __delitem__(self, key):
        if key == 'recipe_name':
            self.source = ''
        if key in __class__.orf_keys:
            del self.__dict__['_recipe_data'][key]
            self._scan_recipe()
        else:
            del self.__dict__[key]

    @property
    def recipe_data(self):
        return self['_recipe_data']

    @property
    def has_alt_ingredients(self):
        return self._has_alt_ingreds

    def get_ingredients(self, amount_level=0, alt_ingred=None, color=False):
        """Returns a list of ingredient strings.

        args:

        - amount_level: in aticipation of a future feature, this is for multiple
                        recipe yields.

        - alt_ingred: If an alt ingredient is given, it returns the ingredients
                      associated with the particular alt ingredient.
        """
        ingredients = []
        if alt_ingred:
            for item in self['alt_ingredients']:
                try:
                    ingredient_data = item[alt_ingred]
                except KeyError:
                    pass
        else:
            ingredient_data = self['ingredients']

        for item in ingredient_data:
            ingred = Ingredient(item, color=color)
            ingredients.append(str(ingred))
        return ingredients
    
    def print_recipe(self, verb_level=0):
        """Print recipe to standard output."""
        print(color.RECIPENAME
            + self['recipe_name'].title()
            + color.NORMAL
            + "\n")

        self['dish_type'] and print("Dish Type: {}"
                                    .format(str(self['dish_type'])))
        self['prep_time'] and print("Prep time: {}"
                                    .format(mins_to_hours(RecipeNum(self['prep_time']))))
        self['cook_time'] and print("Cook time: {}"
                                    .format(mins_to_hours(RecipeNum(self['cook_time']))))
        self['bake_time'] and print("Bake time: {}"
                                    .format(mins_to_hours(RecipeNum(self['bake_time']))))
        self['ready_in'] and print("Ready in: {}"
                                   .format(mins_to_hours(RecipeNum(self['ready_in']))))
        self['oven_temp'] and print("Oven temp: {} {}"
                                    .format(str(self['oven_temp']['amount']),
                                            self['oven_temp']['unit']))

        if verb_level >= 1:
            self['price'] and print("Price: {}".format(self['price']))
            self['author'] and print("Author: {}".format(self['author']))
            self['source_url'] and print("URL: {}".format(self['source_url']))
            self['category'] and print("Category(s): "
                                     + ", ".join(self['category']))
            self['yields'] and print("Yields: " + str(self['yeilds']))
            if self['notes']:
                print(S_DIV)
                print("NOTES:")
                for note in self['notes']:
                    print(note)

        print(color.LINE + S_DIV + color.TITLE + "\nIngredients:" + color.NORMAL)
        # Put together all the ingredients
        for ingred in self.get_ingredients(color=True):
            print(ingred)
        try:
            for item in self.alt_ingreds:
                print("\n{}{}{}".format(color.TITLE,
                                        item.title(),
                                        color.NORMAL))

                for ingred in self.get_ingredients(alt_ingred=item, color=True):
                    print(ingred)
        except (AttributeError, TypeError):
            pass

        print("\n"
                + color.LINE
                + S_DIV
                + color.TITLE
                + "\nMethod:"
                + color.NORMAL)

        # print steps
        # lots of conditional wrapper mods for pretty steps output
        wrapper = textwrap.TextWrapper(width=60)
        if len(self['steps']) > 9:
            wrapper.initial_indent = ' '
            wrapper.subsequent_indent = '    '
        else:
            wrapper.subsequent_indent = '   '

        for index, step in enumerate(self['steps'], start=1):
            if index >= 10:
                wrapper.initial_indent = ''
                wrapper.subsequent_indent = '    '
            wrap = wrapper.fill(step['step'])
            print("{}{}.{} {}".format(color.NUMBER, index, color.NORMAL, wrap))
    
    def get_method(self):
        steps = []
        for step in self['steps']:
            steps.append(step['step'])
        return steps
    
    def dump_to_screen(self, data_type=None):
        """Dump a data format to screen.
        
        This method is mostly useful for troubleshooting
        and development
        """ 
        if data_type in ('raw', None): 
            PP.pprint(self.recipe_data)
        elif data_type == 'yaml':
            yaml.dump(self['_recipe_data'], sys.stdout)
        elif data_type == 'xml':
            result = etree.tostring(self.xml_root,
                                    xml_declaration=True,
                                    encoding='utf-8',
                                    with_tail=False,
                                    method='xml',
                                    pretty_print=True).decode('utf-8')
            print(result)
        else:
            raise ValueError('data_type argument must be one of '
                             'raw, yaml, or xml')

    
    def save(self, save_as=False):
        """save state of class
        
        If save_as is true, we first check to see if the file already exisist
        so we dont clobber an existing recipe. If not save_as, we assume user
        wants to edit a file in which case we intend to overwrite the file with
        changes.
        """
        if not self.source:
            raise RuntimeError('Recipe has no source to save to')
        elif save_as:
            if self.source in RECIPE_DATA_FILES:
                raise RuntimeError('Recipe already exist with that filename')
        else:
            source = os.path.join(RECIPE_DATA_DIR, self.source)
            stream = io.StringIO()
            yaml.dump(self.recipe_data, stream)
            
            with ZipFile(source, 'w') as zfile:
                zfile.writestr('recipe.yaml', stream.getvalue())
                zfile.writestr('MIMETYPE', 'application/recipe+zip')


class RecipeWebScraper(Recipe):

    def __init__(self, url):
        super().__init__()
        self['source_url'] = url
        self.req = urlopen(url)
        self.soup = bs4.BeautifulSoup(self.req, 'html.parser')
        self._fetch_recipe_name()
        self._fetch_ingredients()
        self._fetch_author()
        self._fetch_method()

    def _fetch_recipe_name(self):
        name_box = self.soup.find('h2', attrs={'class': 'modal-title'})
        self['recipe_name'] = name_box.text.strip()

    def _fetch_ingredients(self):
        ingred_box = self.soup.find_all('ul', attrs={'class': 'ingredient-list'})
        ingred_parser = IngredientParser(return_dict=True)
        ingredients = []
        for item in ingred_box:
            for litag in item.find_all('li'):
                ingred_text = ' '.join(litag.text.strip().split())
                ingred = ingred_parser.parse(ingred_text)
                ingredients.append(ingred)
        self['ingredients'] = ingredients

    def _fetch_method(self):
        method_box = self.soup.find('div', attrs={'class': 'directions-inner container-xs'})
        litags = method_box.find_all('li')
        # last litag is "submit a correction", we dont need that
        del litags[-1]
        recipe_steps = []
        for item in litags:
            step_dict = {}
            step_dict['step'] = item.text.strip()
            recipe_steps.append(step_dict)

        self['steps'] = recipe_steps

    def _fetch_author(self):
        name_box = self.soup.find('h6', attrs={'class': 'byline'})
        recipe_by = name_box.text.strip()
        self['author'] = ' '.join(recipe_by.split(' ')[2:]).strip()


class Ingredient:
    """The ingredient class is used to build an ingredietns object

    :param name: name of the ingredient e.g onion
    :param amount: amount of ingredient
    :param size: size of ingredient
    :param unit: ingredient unit such as tablespoon
    :param prep: prep string if any, such as diced, chopped.. etc...
    """
    def __init__(self, ingredients={}, amount_level=0, color=False):
        self.color = color
        self._name = ingredients['name']
        self._unit = ''
        self._amount = 0
        self._amounts = ingredients.get('amounts', '')
        if self._amounts:
            try: 
                self._amount = RecipeNum(self._amounts[amount_level].get('amount', 0))
            except ValueError:
                self._amount = 0
            self._unit = self._amounts[amount_level]['unit']
        self._size = ingredients.get('size', '')
        self._prep = ingredients.get('prep', '')

    def __str__(self):
        """Turn ingredient object into a string

        Calling string on an ingredient object returns the gramatically
        correct representation of the ingredient object.
        """
        color_number = ''
        color_normal = ''
        if self.color:
            color_number = color.NUMBER
            color_normal = color.NORMAL

        if self._name == 's&p':
                return "Salt and pepper to taste"
        elif self._unit == 'taste':
                return "{} to taste".format(self._name.capitalize())
        elif self._unit == 'pinch':
                return "Pinch of {}".format(self._name)
        elif self._unit == 'splash':
                return "Splash of {}".format(self._name)
        else:
            string = "{}{}{} {} {} {}".format(color_number, self.amount, 
                                                color_normal, self._size, 
                                                self.unit, self.name)
            # the previous line adds unwanted spaces if 
            # values are absent we simply clean that up here.
            cleaned_string = " ".join(string.split())
            if self._prep is '':
                return cleaned_string
            else:
                cleaned_string += ", " + self._prep
                return cleaned_string

    @property
    def name(self):
        if not self._unit or self._unit == 'each':
            return p.plural(self._name, self._amount)
        else:
            return self._name

    @property
    def amount(self):
        return self._amount

    @property
    def unit(self):
        if self._unit == 'each':
            return ''
        elif self._amount > 1:
            if self._unit in CAN_UNITS:
                unit = self._unit.split()
                unit_paren = "({})".format(unit[0] + " " + unit[1])
                unit = unit_paren + unit[2]
                return "{}".format(p.plural(unit))
            else:
                return p.plural(self._unit)
        elif self._amount <= 1:
            if self._unit in CAN_UNITS:
                unit = self._unit.split()
                unit_paren = "({})".format(unit[0] + " " + unit[1])
                unit = unit_paren + " " + unit[2]
                return "{}".format(unit)
            else:
                return self._unit
        else:
            return self._unit

    @property
    def quantity(self):
        return self._amount * ureg


class IngredientParser:
    """Convert an ingredient string into a list or dict

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
                    'amounts': [{'amount': <amount>, 'uniit': <unit>}]
                    'prep': <prep>}

    examples:

    >>> parser = IngredientParser()
    >>> parser.parse('1 tablespoon onion, chopped')
    [1, '', 'tablespoon', 'onion chopped', 'chopped']
    >>> parser.parse('3 large carrots, finely diced')
    ['3', 'large', 'carrot', 'finely diced']
    >>> parser = IngredientParser(return_dict=True)
    >>> parser.parse('1 tablespoon onion chopped')
    {'amounts': [{'amount': 1, 'unit': 'tablespoon'}], 'name': 'onion chopped', 'prep': 'chopped'}
    """
    def __init__(self, return_dict=False):

        self.return_dict = return_dict
        self.punctuation = "!\"#$%&'()*+,-:;<=>?@[\]^_`{|}~"
        self._OUNCE_CAN_RE = re.compile(r'\d+ (ounce|pound) (can|bag)')
        self._PAREN_RE = re.compile(r'\((.*?)\)')

    def _preprocess_string(self, string):
        """preprocess the string"""
        # this special forward slash character (differs from '/') is encounterd
        # on some sites througout the web. There maybe others
        if '⁄' in string:
            string = string.replace('⁄', '/')
        test = self._PAREN_RE.search(string)
        if test:
            print(test.group())
        stripd_punc = self._strip_punctuation(string).lower()
        singular_string = ' '.join(all_singular(stripd_punc.split()))
        return singular_string


    def parse(self, string=''):
        """parse the ingredient string"""
        amount = ''
        size = ''
        unit = ''
        name = ''
        prep = ''
        ingred_list = []
        ingred_dict = {}

        # string preprocessing
        pre_string = self._preprocess_string(string)
        match = self._OUNCE_CAN_RE.search(pre_string)
        if match:
            pre_string = pre_string.replace(match.group(), '')
            unit = match.group()

        ingred_list = pre_string.split()
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


        for item in SIZE_STRINGS:
            if item in ingred_string:
                size = item
                ingred_string = ingred_string.replace(item, '')

        for item in INGRED_UNITS:
            if item in ingred_string.split():
                unit = item
                ingred_string = ingred_string.replace(item, '')

        for item in PREP_TYPES:
            if item in ingred_string:
                prep = item
                ingred_string = ingred_string.replace(item, '')

        if not unit:
            unit = 'each'

        # at this point we are assuming that all elements have been removed
        # from list except for the name. Whatever is left gets joined together
        name = ' '.join(ingred_string.split())
        if name.lower() == 'salt and pepper':
            name = 's&p'
        ingred_dict['amounts'] = [{'amount': amount, 'unit': unit}]
        if size: ingred_dict['size'] = size
        ingred_dict['name'] = name
        if prep: ingred_dict['prep'] = prep

        ingred_list = [amount, size, unit, name, prep]

        if self.return_dict:
            return ingred_dict
        else:
            return ingred_list

    def _strip_punctuation(self, string):
        return ''.join(c for c in string if c not in self.punctuation)

# testing
if __name__ == '__main__':
    r = Recipe('test.recipe')
    r.print_recipe()
    
