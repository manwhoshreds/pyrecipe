"""
	pyrecipe.config.py
	~~~~~~~~~~~~~~~~~~
	pyrecipe configurations and globals
"""

import os
import sys
import pprint
import configparser

from pyrecipe import p, color

config = configparser.ConfigParser()

CONFIG_DIR         = os.path.expanduser('~/.config/pyrecipe/')
DB_FILE            = os.path.expanduser('~/git/pyrecipe/pyrecipe/test.db')
RECIPE_DATA_DIR    = os.path.expanduser('~/.config/pyrecipe/recipe_data/')
CONFIG_FILE        = CONFIG_DIR + 'config'
SCRIPT_DIR         = os.path.dirname(__file__)

# parse config
config.read(CONFIG_FILE)
RECIPE_XML_DIR     = os.path.expanduser(config['paths']['recipe_xml_dir'])
SHOPPING_LIST_FILE = os.path.expanduser(config['paths']['shopping_list_file'])
RAND_RECIPE_COUNT  = config['pyrecipe']['rand_recipe_count']

# env
EDITOR             = os.getenv('EDITOR', 'nano')
VIM_MODE_LINE      = "\n# vim: set expandtab ts=4 syntax=yaml:"

RECIPE_DATA_FILES = []
for item in os.listdir(RECIPE_DATA_DIR):
    RECIPE_DATA_FILES.append(RECIPE_DATA_DIR + item)

PP                   = pprint.PrettyPrinter(compact=True, indent=4)
S_DIV                = color.LINE + "~" * 60 + color.NORMAL
REQUIRED_ORD_KEYS    = ['recipe_name', 'dish_type', 
                        'prep_time', 'ingredients', 'steps']

DISH_TYPES           = ['main', 'side', 'dessert', 'condiment', 'dip', 
			'salad dressing', 'sauce', 'base', 'garnish', 'seasoning']

CULINARY_UNITS       = ['teaspoon', 'tablespoon', 'ounce', 'fulid ounce', 
                        'cup', 'quart', 'gallon', 'pound', 'pint', 'gram', 'mililiter']

PINT_UNDEFINED_UNITS = ['box', 'to taste', 'inch piece', 'stick', 'bottle', 'each', 'bag',
                        'whole', 'link', 'sprig', 'stalk', 'pinch of', 'cube', 'splash of']

CAN_UNITS = ['TEST']
# CAN_UNITS are checked later and put in parenthesis
# its not considered professional recipe writing
# to use two numbers in a row, for example "1 32 ounce can"

_ingr_units          = CULINARY_UNITS + PINT_UNDEFINED_UNITS
_nonplurals          = ('each', 'splash')
_plur_units          = [p.plural(x) for x in _ingr_units if x not in _nonplurals]
_size_strs           = ['large', 'medium', 'small', 'heaping']
_prp_typs            = ['softened', 'diced', 'finely diced', 'shredded', 
                        'tightly packed', 'drained', 'drained and rinsed', 
                        'deviened', 'cubed', 'chopped', 'finely chopped', 
                        'freshly ground', 'very finely chopped', 'minced', 'finely minced', 
                        'peeled and finely minced', 'sliced', 'grated', 
                        'squeezed', 'freshly grated', 'peeled', 'quartered', 
                        'julienned', 'puréed', 'crushed', 'coarsely chopped', 
                        'coarsely cracked', 'cut up', 'melted', 'seeded and deviened', 
                        'cut into 2 inch pieces', 'cut into 1 inch pieces', 
                        'cut into 1 inch lengths', 'uncooked', 'peeled and grated', 
                        'lightly packed', 'thinly sliced', 'finely sliced', 'roasted',
                        'boiling']

INGRED_UNITS          = sorted(_ingr_units + _plur_units)
SIZE_STRINGS          = sorted(_size_strs)
PREP_TYPES            = sorted(_prp_typs)

if __name__ == '__main__':
    print(INGRED_UNITS)
