# -*- coding: utf-8 -*-
"""
    pyrecipe
    ~~~~~~~~

    Pyrecipe is a python application that lets you manage recipes.

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""

import os

from pint import UnitRegistry
#import inflect
from ruamel.yaml import YAML
yaml = YAML(typ='safe')
yaml.default_flow_style = False

from pyrecipe import utils
from .config import (__version__, __scriptname__, 
                     DB_FILE, RECIPE_DATA_FILES)

ureg = UnitRegistry()
ureg.load_definitions(os.path.expanduser('~/.local/lib/python3.6/site-packages/pyrecipe/culinary_units.txt'))

Q_ = ureg.Quantity
color = utils.Color()

from .recipe import Recipe

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
                self.recipe_names.append(_recipe['recipe_name'])
                if _recipe['dish_type'] == 'main':
                    self.maindish_names.append(_recipe['recipe_name'])
                if  _recipe['dish_type'] == 'salad dressing':
                    self.dressing_names.append(_recipe['recipe_name'])
                if _recipe['dish_type'] == 'sauce':
                    self.sauce_names.append(_recipe['recipe_name'])
                if _recipe['dish_type'] == 'salad':
                    self.salad_names.append(_recipe['recipe_name'])

manifest = RecipeManifest()

                



