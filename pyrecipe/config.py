"""
	pyrecipe.config.py
	~~~~~~~~~~~~~~~~~~
	pyrecipe configurations and globals
"""

import os
import shutil
import pprint
import configparser

#python_binary = shutil.which('python')

CONFIG_DIR = os.path.expanduser('~/.config/pyrecipe/')
#if python_binary == '/usr/bin/python':
RECIPE_DATA_DIR = os.path.join(CONFIG_DIR, 'recipe_data/')
DB_FILE = os.path.join(CONFIG_DIR, 'recipes.db')
#else:
#    RECIPE_DATA_DIR = os.path.expanduser('~/git/pyrecipe/test/recipe_data/')
#    DB_FILE = os.path.expanduser('~/git/pyrecipe/test/recipes_test.db')

CONFIG_FILE = os.path.join(CONFIG_DIR + 'pyrecipe.cfg')
SCRIPT_DIR = os.path.dirname(__file__)

# parse config
config = configparser.ConfigParser()
config.read(CONFIG_FILE)
RECIPE_XML_DIR = os.path.expanduser(config['paths']['recipe_xml_dir'])
SHOPPING_LIST_FILE = os.path.expanduser(config['paths']['shopping_list_file'])
RAND_RECIPE_COUNT = config['pyrecipe']['rand_recipe_count']

RECIPE_DATA_FILES = []
for item in os.listdir(RECIPE_DATA_DIR):
    RECIPE_DATA_FILES.append(RECIPE_DATA_DIR + item)

PP = pprint.PrettyPrinter(compact=True, indent=4)

CULINARY_UNITS = [
    'teaspoon', 'tablespoon', 'ounce', 'fulid ounce', 
    'cup', 'quart', 'gallon', 'pound', 'pint', 'gram', 'mililiter'
]
PINT_UNDEFINED_UNITS = [
    'box', 'to taste', 'inch piece', 'stick', 'bottle', 'each', 'bag',
    'whole', 'link', 'sprig', 'stalk', 'pinch of', 'cube', 'splash of'
]

_ingr_units = CULINARY_UNITS + PINT_UNDEFINED_UNITS
_nonplurals = ('each', 'splash')
_plur_units = [x + 's' for x in _ingr_units if x not in _nonplurals]
_size_strs = ['large', 'medium', 'small', 'heaping']
_prp_typs = [
    'softened', 'diced', 'finely diced', 'shredded', 'tightly packed', 
    'drained', 'drained and rinsed', 'deviened', 'cubed', 'chopped', 
    'finely chopped', 'freshly ground', 'very finely chopped', 'minced', 
    'finely minced', 'peeled and finely minced', 'sliced', 'grated', 'squeezed',
    'freshly grated', 'peeled', 'quartered', 'julienned', 'puréed', 'crushed', 
    'coarsely chopped', 'coarsely cracked', 'cut up', 'melted', 
    'seeded and deviened', 'uncooked', 'peeled and grated', 'lightly packed', 
    'thinly sliced', 'finely sliced', 'roasted', 'boiling'
]

INGRED_UNITS          = sorted(_ingr_units + _plur_units)
SIZE_STRINGS          = sorted(_size_strs)
PREP_TYPES            = sorted(_prp_typs)

if __name__ == '__main__':
    print(python_binary)
    #print(INGRED_UNITS)
