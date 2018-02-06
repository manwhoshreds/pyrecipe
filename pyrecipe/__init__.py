# -*- coding: utf-8 -*-
"""
    pyrecipe
    ~~~~~~~~

    Pyrecipe is a python application that lets you manage recipes.
    Recipe are saved in Yaml format.

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""

import os
import sys
from numbers import Number
from fractions import Fraction
from math import ceil
from zipfile import ZipFile

from pint import UnitRegistry
from ruamel.yaml import YAML
import inflect

from pyrecipe.config import (__version__, __scriptname__, 
                     DB_FILE, RECIPE_DATA_FILES)
from .recipe_numbers import RecipeNum


yaml = YAML(typ='safe')
yaml.default_flow_style = False

ureg = UnitRegistry()
ureg.load_definitions(os.path.expanduser('~/.local/lib/python3.6/site-packages/pyrecipe/culinary_units.txt'))
#Q_ = ureg.Quantity

class Q_(ureg.Quantity):
    """subclass to implement a few custom behaviors
    
    Capabilities include alway rounding up to the nearest whole
    an printing plural units dependent upon the objects magnitude
    """

    def round_up(self):
        return self.__class__(ceil(self._magnitude), self._units)

    def __str__(self):
        if str(self.units) == 'each':
            return format(self)
        elif self.magnitude > 1:
            return '{} {}'.format(self.magnitude, p.plural(str(self.units)))
        else:
            return format(self)
        

class RecipeManifest:

    def __init__(self):
        self.recipe_names = []
        self.maindish_names = []
        self.dressing_names = []
        self.sauce_names = []
        self.salad_names = []
        self.recipe_authors = []
        self.urls = []
        for item in RECIPE_DATA_FILES:
            #with ZipFile(item, 'r') as zfile:
            #    try: 
            with open(item, 'r') as stream:
                _recipe = yaml.load(stream)
                self.recipe_names.append(_recipe['recipe_name'].lower())
                if _recipe['dish_type'] == 'main':
                    self.maindish_names.append(_recipe['recipe_name'])
                if _recipe['dish_type'] == 'salad dressing':
                    self.dressing_names.append(_recipe['recipe_name'])
                if _recipe['dish_type'] == 'sauce':
                    self.sauce_names.append(_recipe['recipe_name'])
                if _recipe['dish_type'] == 'salad':
                    self.salad_names.append(_recipe['recipe_name'])
            #    except KeyError:
            #        sys.exit('cannot find recipe.yaml')

manifest = RecipeManifest()

class Color:
    """
       The color class defines various colors for 
       use in pyrecipe output.
    """
    
    NORMAL = '\033[m'
    ERROR = '\033[1;31m'
    RECIPENAME = '\033[1;36m'
    TITLE = '\033[36m'
    NUMBER = '\033[1;33m'
    REGULAR = '\033[1;35m'
    LINE = '\033[1;37m'
    INFORM = '\033[1;36m'

color = Color()


# Inflects default behaviour for returning the singular of a word is
# not very useful to this project because it returns false if
# it comes across a non-noun word. Therfore, the following is a
# functional work-a-round
class InflectEngine(inflect.engine):

    def __init__(self):
        super().__init__()
        self.ignored = ['roma', 'canola', 'hummus']

    def singular_noun(self, word):
        if word in self.ignored:
            return word

        singular = super().singular_noun(word)
        if singular:
            return singular
        else:
            return word

    def plural(self, word, count=None):
        if count: 
            if count <= 1:
                return word
            else:
                word = super().plural(word)
                return word
        else:
            word = super().plural(word)
            return word

p = InflectEngine()
