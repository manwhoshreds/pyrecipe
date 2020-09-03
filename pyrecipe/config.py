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
if os.path.isfile(_conf):
    CONFIG_FILE = _conf
else:
    CONFIG_FILE = '/etc/pyrecipe/pyrecipe.cfg'

RECIPE_DATA_DIR = os.path.join(_usr_config_path, 'recipe_data/')
DB_FILE = os.path.join(_usr_config_path, 'recipes.db')
SCRIPT_DIR = os.path.dirname(__file__)

RECIPE_DATA_FILES = []
for item in os.listdir(RECIPE_DATA_DIR):
    RECIPE_DATA_FILES.append(RECIPE_DATA_DIR + item)

PP = pprint.PrettyPrinter(compact=True, indent=4)
SIZE_STRINGS = ['large', 'medium', 'small', 'heaping']

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
USER_EMAIL = config['pyrecipe'].get('user_email', None)
USER_NAME = config['pyrecipe'].get('user_name', None)
def get_random_picks():
    picks = config['pyrecipe'].get('random_picks', None)
    random_picks = {}
    if picks:
        picks = picks.split()
        #for item in picks:
        #    dt, num = item.split()
        #    random_picks[dt] = num
        return random_picks

RANDOM_PICKS = get_random_picks()
#print(RANDOM_PICKS)

# --End user config

if __name__ == '__main__':
    pass
