
import os
import sys
import yaml
import pprint

# Script constants
__version__     = '0.3.7'
__scriptname__  = os.path.basename(sys.argv[0])
__email__       = "m.k.miller@gmx.com"

#---GLOBALS--------
CONFIG_FILE     = os.path.expanduser('~/.config/pyrecipe/config')
DB_FILE         = os.path.expanduser('~/.config/pyrecipe/recipe.db')
RECIPE_DATA_DIR = os.path.expanduser('~/.config/pyrecipe/recipe_data/')
#HASH_FILE      = os.path.expanduser('~/.local/')

with open(CONFIG_FILE, "r") as stream:
	try:
		settings = yaml.safe_load(stream)
		RECIPE_XML_DIR = os.path.expanduser(settings['recipe_xml_dir'])
		RAND_RECIPE_COUNT = settings['rand_recipe_count']
		SHOPPING_LIST_FILE = os.path.expanduser(settings['shopping_list_file'])
	except yaml.YAMLError as exc:
		print(exc)
		sys.exit(1)

RECIPE_FILES = []
for item in os.listdir(RECIPE_DATA_DIR):
	RECIPE_FILES.append(RECIPE_DATA_DIR + item)

# gather salad and main dish recipes	
MAINDISH_FILES = []
DRESSING_FILES = []
DESSERT_FILES = []
SIDE_FILES = []
for item in RECIPE_FILES:
	with open(item, "r") as stream:
		try:
			recipe = yaml.safe_load(stream)
			dtype = recipe['dish_type']
		except yaml.YAMLError as exc:
			print(exc)
			sys.exit(0)
	if dtype == "main":
		MAINDISH_FILES.append(item)
	elif dtype == "salad dressing":
		DRESSING_FILES.append(item)
	elif dtype == "side":
		SIDE_FILES.append(item)
	else:
		continue

PP                   = pprint.PrettyPrinter(indent=4)
P_DIV                = "*" * 50
S_DIV                = "~" * 50
REQUIRED_ORD_KEYS    = ['recipe_name', 'dish_type', 'prep_time', 'ingredients', 'steps']
DISH_TYPES           = ['main', 'side', 'dessert', 'condiment', 'dip', 
						  'salad dressing', 'sauce', 'base', 'garnish', 'seasoning']
CULINARY_UNITS       = ['teaspoon', 'tablespoon', 'ounce', 'cup', 'quart', 'gallon', 'pound', 'pint']
PINT_UNDEFINED_UNITS = ['box', 'taste', 'inch piece', 'stick', 'bottle', 'each', 'bag',
                        'whole', 'link', 'sprig', 'stalk', 'can', 'pinch', 'cube', 'splash']
# QUANTITY_UNITS are checked later and put in parenthesis
# its not considered professional recipe writing
# to use two numbers in a row like "1 32 ounce can"
CAN_UNITS         = ['32 ounce can', '16 ounce can', '15 ounce can', '8.5 ounce can', '8 ounce can', '2 pound package']
ALLOWED_INGRED_UNITS   = CAN_UNITS + CULINARY_UNITS + PINT_UNDEFINED_UNITS
PREP_TYPES             = ['softened', 
                          'diced', 
						  'finely diced', 
						  'shredded', 
						  'tightly packed', 
						  'drained', 
						  'deviened', 
						  'cubed', 
						  'chopped', 
						  'finely chopped', 
						  'freshly ground', 
						  'very finely chopped', 
						  'minced', 
						  'finely minced', 
						  'peeled and finely minced', 
						  'sliced', 
						  'grated', 
						  'squeezed', 
						  'freshly grated', 
						  'peeled', 
						  'quartered', 
						  'julienned', 
						  'puréed', 
						  'crushed', 
						  'coarsely chopped', 
						  'coarsely cracked', 
						  'cut up', 
						  'melted', 
						  'seeded and deviened', 
						  'cut into 2 inch pieces', 
						  'cut into 1 inch pieces', 
						  'cut into 1 inch lengths', 
						  'uncooked',
						  'peeled and grated',
						  'lightly packed',
						  'roasted']
