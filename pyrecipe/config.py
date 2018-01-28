"""
	pyrecipe.config.py
	~~~~~~~~~~~~~~~~~~
	pyrecipe configurations and globals
"""

import os
import sys
import pprint
import configparser


__version__     = '0.7.8'
__email__       = "m.k.miller@gmx.com"
__scriptname__  = os.path.basename(sys.argv[0])

config = configparser.ConfigParser()

#---GLOBALS--------
CONFIG_DIR         = os.path.expanduser('~/.config/pyrecipe/')
RECIPE_DATA_DIR    = CONFIG_DIR + 'recipe_data/'
CONFIG_FILE        = CONFIG_DIR + 'config'
SCRIPT_DIR         = os.path.dirname(__file__)

# parse config
config.read(CONFIG_FILE)
RECIPE_XML_DIR     = os.path.expanduser(config['paths']['recipe_xml_dir'])
DB_FILE            = os.path.expanduser(config['paths']['recipe_db_file'])
SHOPPING_LIST_FILE = os.path.expanduser(config['paths']['shopping_list_file'])
RAND_RECIPE_COUNT  = config['pyrecipe']['rand_recipe_count']

# env
EDITOR             = os.getenv('EDITOR', 'nano')
VIM_MODE_LINE      = "\n# vim: set expandtab ts=4 syntax=yaml:"

RECIPE_DATA_FILES = []
for item in os.listdir(RECIPE_DATA_DIR):
    RECIPE_DATA_FILES.append(RECIPE_DATA_DIR + item)

PP                   = pprint.PrettyPrinter(compact=True, indent=4)
S_DIV                = "~" * 60
REQUIRED_ORD_KEYS    = ['recipe_name', 'dish_type', 
                        'prep_time', 'ingredients', 'steps']
DISH_TYPES           = ['main', 'side', 'dessert', 'condiment', 'dip', 
			'salad dressing', 'sauce', 'base', 'garnish', 'seasoning']
CULINARY_UNITS       = ['teaspoon', 'tablespoon', 'ounce', 'fulid ounce', 
                        'cup', 'quart', 'gallon', 'pound', 'pint', 'gram', 'mililiter']
PINT_UNDEFINED_UNITS = ['box', 'taste', 'inch piece', 'stick', 'bottle', 'each', 'bag',
                        'whole', 'link', 'sprig', 'stalk', 'can', 'pinch', 'cube', 'splash']
# CAN_UNITS are checked later and put in parenthesis
# its not considered professional recipe writing
# to use two numbers in a row, for example "1 32 ounce can"
CAN_UNITS            = ['32 ounce can', '16 ounce can', '15 ounce can', '8.5 ounce can', '8 ounce can', '2 pound package']

_ingr_units          = CAN_UNITS + CULINARY_UNITS + PINT_UNDEFINED_UNITS
_size_strs           = ['large', 'medium', 'small', 'heaping']
_prp_typs            = ['softened', 'diced', 'finely diced', 'shredded', 
                        'tightly packed', 'drained', 'drained and rinsed', 
                        'deviened', 'cubed', 'chopped', 'finely chopped', 'freshly ground', 
                        'very finely chopped', 'minced', 'finely minced', 
                        'peeled and finely minced', 'sliced', 'grated', 
                        'squeezed', 'freshly grated', 'peeled', 'quartered', 
                        'julienned', 'puréed', 'crushed', 'coarsely chopped', 
                        'coarsely cracked', 'cut up', 'melted', 'seeded and deviened', 
                        'cut into 2 inch pieces', 'cut into 1 inch pieces', 
                        'cut into 1 inch lengths', 'uncooked', 'peeled and grated', 
                        'lightly packed', 'thinly sliced', 'finely sliced', 'roasted']

INGRED_UNITS          = sorted(_ingr_units)
SIZE_STRINGS          = sorted(_size_strs)
PREP_TYPES            = sorted(_prp_typs)
