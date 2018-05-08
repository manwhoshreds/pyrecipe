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


    - RecipeWebScraper: The pyrecipe web_scraper class is a web
                        scraping utility used to download and analyze
                        recipes found on websites in an attempt to
                        save the recipe data in the format understood
                        by pyrecipe.
                        Currently supported sites: www.geniuskitchen.com
    * Inherits from Recipe

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

import lxml.etree as ET
from termcolor import colored
from ruamel.yaml import YAML

import pyrecipe.utils as utils
import pyrecipe.config as config
from pyrecipe.db import update_db
from pyrecipe.recipe_numbers import RecipeNum

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
    the reicpe file.    
    """
    # All keys applicable to the Open Recipe 
    ORF_KEYS = [
        'recipe_name', 'recipe_uuid', 'dish_type', 'category',
        'cook_time', 'prep_time', 'author', 'oven_temp', 'bake_time',
        'yields', 'ingredients', 'alt_ingredients', 'notes',
        'source_url', 'steps', 'tags', 'source_book', 'price'
    ]

    def __init__(self, source=''):
        self.source = utils.get_source_path(source)
        if self.source:
            try:
                with ZipFile(self.source, 'r') as zfile:
                    try:
                        with zfile.open('recipe.yaml', 'r') as stream:
                            self._recipe_data = yaml.load(stream)
                    except KeyError:
                        sys.exit(utils.msg("Can not find recipe.yaml. Is this"
                                           " really a recipe file?", "ERROR"))
            except BadZipFile as e:
                sys.exit(utils.msg("{}".format(e), "ERROR"))
        else:
            self._recipe_data = {}
            # dish type should default to main
            self['dish_type'] = 'main'
            self['recipe_uuid'] = str(uuid.uuid4())
            self.source = utils.get_file_name_from_uuid(self['recipe_uuid'])

        # Scan the recipe to build the xml
        self._scan_recipe()

    def _scan_recipe(self):
        """Scan the recipe to build xml."""
        self.root_keys = list(self._recipe_data.keys())
        self.xml_root = ET.Element('recipe')
        self.xml_root.set('name', self['recipe_name'])

        ingredients, alt_ingredients = self.get_ingredients()
        # Not interested in adding notes to xml, maybe in the future
        for item in self.root_keys:
            if item not in ('ingredients', 'alt_ingredients', 'notes',
                            'steps', 'recipe_name', 'category'):
                xml_entry = ET.SubElement(self.xml_root, item)
                xml_entry.text = str(self[item])

        # ready_in
        # not actually an ord tag, so is not read from recipe file
        # it is simply calculated within the class
        if self['prep_time'] and self['cook_time']:
            self['ready_in'] = RecipeNum(
                self['prep_time']) + RecipeNum(self['cook_time']
            )
        elif self['prep_time'] and self['bake_time']:
            self['ready_in'] = RecipeNum(
                self['prep_time']) + RecipeNum(self['bake_time']
            )
        else:
            self['ready_in'] = self['prep_time']

        # oven_temp
        if self['oven_temp']:
            self.oven_temp = self['oven_temp']
            self.ot_amount = self['oven_temp']['amount']
            self.ot_unit = self['oven_temp']['unit']
            xml_oven_temp = ET.SubElement(self.xml_root, "oven_temp")
            xml_oven_temp.text = str(self.ot_amount) + " " + str(self.ot_unit)

        # ingredients
        if ingredients:
            xml_ingredients = ET.SubElement(self.xml_root, "ingredients")
            for ingred in ingredients:
                xml_ingred = ET.SubElement(xml_ingredients, "ingred")
                xml_ingred.text = ingred

        # alt_ingredients 
        if alt_ingredients:
            for item in alt_ingredients:
                xml_alt_ingredients = ET.SubElement(self.xml_root, "alt_ingredients")
                xml_alt_ingredients.set('alt_name', item)
                for ingred in alt_ingredients[item]:
                    xml_alt_ingred = ET.SubElement(xml_alt_ingredients, "ingred")
                    xml_alt_ingred.text = ingred

        xml_steps = ET.SubElement(self.xml_root, "steps")
        for step in self['steps']:
            steps_of = ET.SubElement(xml_steps, "step")
            steps_of.text = step['step']

    def __repr__(self):
        return "Recipe(name='{}')".format(self['recipe_name'])

    def __getitem__(self, key):
        if key in Recipe.ORF_KEYS:
            return self.__dict__['_recipe_data'].get(key, '')
        else:
            return self.__dict__.get(key, '')

    def __setitem__(self, key, value):
        if key == 'oven_temp':
            value = value.split()
            try:
                assert len(value) == 2
            except AssertionError:
                raise RuntimeError("oven_temp format must be '300 F'")
            self.__dict__['_recipe_data'][key] = {
                'amount': value[0],
                'unit': value[1]
            }
            self._scan_recipe()
        elif key in Recipe.ORF_KEYS:
            self.__dict__['_recipe_data'][key] = value
            self._scan_recipe()
        else:
            self.__dict__[key] = value

    def __delitem__(self, key):
        if key in Recipe.ORF_KEYS:
            try:
                del self.__dict__['_recipe_data'][key]
            except KeyError:
                pass
            self._scan_recipe()
        else:
            del self.__dict__[key]

    def __hash__(self):
        """Get the recipe hash."""
        return hash(self.get_yaml_string())

    @property
    def ingredients(self):
        """Return ingredient data."""
        return self['ingredients']

    @ingredients.setter
    def ingredients(self, value):
        """Set the ingredients of a recipe."""
        if not isinstance(value, list):
            raise TypeError('Ingredients must be a list')

        ingred_parser = IngredientParser()
        ingredients = []
        for item in value:
            ingred = ingred_parser.parse(item)
            ingredients.append(ingred)

        self['ingredients'] = ingredients
        self._scan_recipe()

    @property
    def alt_ingredients(self):
        """Return alt ingredient data."""
        return self['alt_ingredients']

    @alt_ingredients.setter
    def alt_ingredients(self, value):
        """Set alt ingredients."""
        if not isinstance(value, list):
            raise TypeError('Alt Ingredients must be a list')
        if not isinstance(value[0], dict):
            raise TypeError('Alt Ingredients must be a list of dicts')

        ingred_parser = IngredientParser()
        alt_ingredients = []
        for item in value:
            alt_name = list(item.keys())[0]
            ingreds = list(item.values())[0]
            parsed_ingreds = []
            entry = {}
            for ingred in ingreds:
                parsed = ingred_parser.parse(ingred)
                parsed_ingreds.append(parsed)
            entry[alt_name] = parsed_ingreds
            alt_ingredients.append(entry)

        self['alt_ingredients'] = alt_ingredients
        self._scan_recipe()

    def get_xml_data(self):
        """Return the xml data."""
        result = ET.tostring(
            self.xml_root,
            xml_declaration=True,
            encoding='utf-8',
            with_tail=False,
            method='xml',
            pretty_print=True
        )
        return result.decode('utf-8')

    def get_ingredients(self, amount_level=0, color=False):
        """Return a list of ingredient strings.

        args:

        - amount_level: in aticipation of a future feature, this is for multiple
                        recipe yields.
        """
        ingredients = []
        for item in self['ingredients']:
            ingred = Ingredient(
                item, 
                color=color,
                amount_level=amount_level
            )
            ingredients.append(str(ingred))

        named_ingredients = OrderedDict()
        if self['alt_ingredients']:
            alt_ingreds = self['alt_ingredients']
            for item in alt_ingreds:
                alt_name = list(item.keys())[0]
                ingred_list = []
                for ingredient in list(item.values())[0]:
                    ingred = Ingredient(
                        ingredient, 
                        color=color,
                        amount_level=amount_level
                    )
                    ingred_list.append(str(ingred))
                named_ingredients[alt_name] = ingred_list

        return ingredients, named_ingredients

    def print_recipe(self, verbose=False, amount_level=0):
        """Print recipe to standard output."""
        print(self.__str__(verbose, amount_level))
    
    def __str__(self, verbose=False, amount_level=0):
        recipe_str = colored(self['recipe_name'].title(), 'cyan', attrs=['bold'])
        recipe_str += "\n\nDish Type: {}".format(str(self['dish_type']))
        for item in ('prep_time', 'cook_time', 'bake_time', 'ready_in'):
            if self[item]:
                recipe_str += "\n{}: {}".format(item.replace('_', ' ').title(),
                              utils.mins_to_hours(RecipeNum(self[item])))

        if self['oven_temp']:
            tmp = str(self['oven_temp']['amount'])
            unt = self['oven_temp']['unit']
            recipe_str += "\nOven temp: {} {}".format(tmp, unt)

        if self['author']:
            recipe_str += "\nAuthor: {}".format(self['author'])
        
        extra_info = False
        if verbose:
            if self['price']:
                recipe_str += "\nPrice: {}".format(self['price'])
                extra_info = True
            if self['source_url']:
                recipe_str += "\nURL: {}".format(self['source_url'])
                extra_info = True
            if self['category']:
                recipe_str += ("\nCategory(s): {}"
                               .format(", ".join(self['category'])))
                extra_info = True
            if self['yields']:
                recipe_str += ("\nYields: " + str(self['yeilds']))
                extra_info = True
            if self['notes']:
                recipe_str += colored("\n\nNotes:", "cyan")
                wrapped = utils.wrap(self['notes'])
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
        ingreds, alt_ingreds = self.get_ingredients(
            color=True,
            amount_level=amount_level
        )
        for ingred in ingreds:
            recipe_str += "\n{}".format(ingred)
        
        if alt_ingreds:
            for item in alt_ingreds:
                recipe_str += colored("\n\n{}".format(item.title()), "cyan")

                for ingred in alt_ingreds[item]:
                    recipe_str += "\n{}".format(ingred)
        
        recipe_str += "\n\n{}".format(utils.S_DIV(79))
        recipe_str += colored("\nMethod:", "cyan", attrs=["underline"])

        # print steps
        wrapped = utils.wrap(self.get_method())
        for index, step in wrapped:
            recipe_str += "\n{}".format(colored(index, "yellow"))
            recipe_str += step

        return recipe_str

    def get_method(self):
        """Return a list of steps."""
        steps = []
        for step in self['steps']:
            steps.append(step['step'])
        return steps

    def dump_to_screen(self, data_type=None):
        """Dump a data format to screen.

        This method is mostly useful for troubleshooting
        and development. It prints data in three formats.
        raw (just a plain python dictionary with pretty print)
        yaml, and xml.
        """
        if data_type in ('raw', None):
            config.PP.pprint(self['_recipe_data'])
        elif data_type == 'yaml':
            yaml.dump(self['_recipe_data'], sys.stdout)
        elif data_type == 'xml':
            print(self.get_xml_data())
        else:
            raise ValueError('data_type argument must be one of '
                             'raw, yaml, or xml')

    def get_yaml_string(self):
        string = io.StringIO()
        yaml.dump(self['_recipe_data'], string)
        return string.getvalue()
   
    @update_db
    def save(self):
        """save state of class."""
        if not self.source:
            raise RuntimeError('Recipe has no source to save to')
        else:
            stream = io.StringIO()
            yaml.dump(self['_recipe_data'], stream)

            with ZipFile(self.source, 'w') as zfile:
                zfile.writestr('recipe.yaml', stream.getvalue())
                zfile.writestr('MIMETYPE', 'application/recipe+zip')


class Ingredient:
    """Build an Ingredient object.

    Given a dict of ingredient data, Ingredient class can return a string
    :param ingredient: dict of ingredient data
    :param amount_level: choose the yield of the recipe
    :param color: return string with color data for color output
    """
    def __init__(self, ingredient={}, amount_level=0, color=False):
        if not isinstance(ingredient, dict):
            raise TypeError('Ingredient only except dict as its first argument')
        self.color = color
        self.name = ingredient['name']
        self.size = ingredient.get('size', '')
        self.prep = ingredient.get('prep', '')
        self.note = ingredient.get('note', '')
        self.amount = ''
        self.unit = ''
        self.amounts = ingredient.get('amounts', '')
        if self.amounts:
            try: 
                self.amount = RecipeNum(self.amounts[amount_level].get('amount', ''))
            except ValueError:
                self.amount = ''
            self.unit = self.amounts[amount_level]['unit']
        if self.unit == 'each':
            self.unit = ''

    def __str__(self):
        """Turn ingredient object into a string

        Calling string on an ingredient object returns the gramatically
        correct representation of the ingredient object.
        """
        color_number = None
        color_note = None
        if self.color:
            color_number = 'yellow'
            color_note = 'cyan'
        
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

        for item in config.INGRED_UNITS:
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
    color = False
    colored = colored if color else lambda a, kw: None
    print(colored)
    #req = urlopen('http://test')
    #print(req)
    
