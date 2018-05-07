# -*- encoding: UTF-8 -*-
"""
    pyrecipe.webscraper
    ~~~~~~~~~~~~~~~~~~~
    The recipe module contains the main recipe
    class used to interact with ORF (open recipe format) files.
    You can simply print the recipe or print the xml dump.

    - RecipeWebScraper: The pyrecipe web_scraper class is a web
                        scraping utility used to download and analyze
                        recipes found on websites in an attempt to
                        save the recipe data in the format understood
                        by pyrecipe.
                        Currently supported sites: www.geniuskitchen.com
    * Inherits from Recipe

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""
import re
import io
import sys
import uuid
import string
from collections import OrderedDict
from urllib.request import urlopen
from urllib.parse import urlencode
from zipfile import ZipFile, BadZipFile

import bs4
import lxml.etree as ET
from termcolor import colored
from ruamel.yaml import YAML

import pyrecipe.utils as utils
import pyrecipe.config as config
from pyrecipe.db import update_db
from pyrecipe.recipe_numbers import RecipeNum


class RecipeWebScraper(Recipe):
    """Scrape recipes from a web source.
    
    Main use is to make a template for a recipe on which
    to develop further.
    """
    def __init__(self, url):
        super().__init__()
        self['source_url'] = url
        try:
            self.req = urlopen(url)
        except ValueError:
            sys.exit('You must supply a valid url.')
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
        ingred_parser = IngredientParser()
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
    req = urlopen('test')
    print(req)
    
