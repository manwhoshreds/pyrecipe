# -*- coding: utf-8 -*-
"""
    pyrecipe
    ~~~~~~~~

    Pyrecipe is a python application that lets you manage recipes.
    Recipe are saved in Yaml format.

    copyright: 2017 by Michael Miller
    license: GPL, see LICENSE for more details.
"""

import os
from numbers import Number
from fractions import Fraction

from pint import UnitRegistry
ureg = UnitRegistry()
ureg.load_definitions(os.path.expanduser('~/.local/lib/python3.6/site-packages/pyrecipe/culinary_units.txt'))
Q_ = ureg.Quantity

from ruamel.yaml import YAML
yaml = YAML(typ='safe')
yaml.default_flow_style = False

from pyrecipe.config import (__version__, __scriptname__, 
                     DB_FILE, RECIPE_DATA_FILES)


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

manifest = RecipeManifest()


class RecipeNum:

    def __init__(self, number=''):
        if isinstance(number, str):
            for slash in '/⁄':
                if slash in number: 
                    num, den = number.split(slash) 
                    self.number = Fraction(int(num), int(den))
                    break
                elif '.' in number:
                    self.number = float(number)
                else:
                    try:
                        self.number = int(number)
                    except ValueError:
                        self.number = number
        elif isinstance(number, int):
            self.number = number
        elif isinstance(number, float):
            self.number = number
        else:
            self.number = number
    
    def __repr__(self):
        return self.number

    @property 
    def isnumber(self):
        if isinstance(self.number, Number):
            return True
        else:
            return False
    
    @property
    def value(self):
        return self.number

