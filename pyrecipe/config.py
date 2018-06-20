"""
	pyrecipe.config.py
	~~~~~~~~~~~~~~~~~~
	pyrecipe configurations and globals
"""
import os
import pprint
import configparser


# start pyrecipe config
#-- file paths --
_usr_config_path = os.path.expanduser('~/.config/pyrecipe')
_recipe_data_path = os.path.join(_usr_config_path, 'recipe_data/')
if not os.path.exists(_usr_config_path):
    os.makedirs(_usr_config_path)
    os.makedirs(_recipe_data_path)

_conf = os.path.join(_usr_config_path, 'pyrecipe.cfg')
if os.path.exists(_conf):
    CONFIG_FILE = _conf
else:
    CONFIG_FILE = '/etc/pyrecipe/pyrecipe.cfg'

RECIPE_DATA_DIR = os.path.join(_usr_config_path, 'recipe_data/')
DB_FILE = os.path.join(_usr_config_path, 'recipes.db')
SCRIPT_DIR = os.path.dirname(__file__)

# start user config
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# --Paths
_userdir = os.path.expanduser
RECIPE_XML_DIR = _userdir(config['paths'].get('recipe_xml_dir', None))
SHOPPING_LIST_FILE = _userdir(config['paths'].get('shopping_list_file', None))

# --Pyrecipe
RAND_RECIPE_COUNT = config['pyrecipe'].get('rand_recipe_count', 4)
PYRECIPE_COLOR = config['pyrecipe'].get('color', None)
USER_NAME = config['pyrecipe'].get('user_name', None)

# --End user config

RECIPE_DATA_FILES = []
for item in os.listdir(RECIPE_DATA_DIR):
    RECIPE_DATA_FILES.append(RECIPE_DATA_DIR + item)

PP = pprint.PrettyPrinter(compact=True, indent=4)

#CULINARY_UNITS = [
#    'teaspoon', 'tablespoon', 'ounce', 'fulid ounce', 
#    'cup', 'quart', 'gallon', 'pound', 'pint', 'gram', 'mililiter'
#]
#PINT_UNDEFINED_UNITS = [
#    'box', 'to taste', 'inch piece', 'stick', 'bottle', 'each', 'bag',
#    'whole', 'link', 'sprig', 'stalk', 'pinch of', 'cube', 'splash of'
#]

#_ingr_units = CULINARY_UNITS + PINT_UNDEFINED_UNITS
#_nonplurals = ('each', 'splash')
#_plur_units = [x + 's' for x in _ingr_units if x not in _nonplurals]
#_size_strs = ['large', 'medium', 'small', 'heaping']

#INGRED_UNITS = sorted(_ingr_units + _plur_units)
#SIZE_STRINGS = sorted(_size_strs)

if __name__ == '__main__':
    pass
    #print(INGRED_UNITS)
