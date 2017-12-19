"""
	utils for the pyrecipe program

"""
import os
from .config import *
#from .recipe import *



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

def num(n):
	try:
		return int(n)
	except ValueError:
		return float(n)

def get_file_name(recipe):
	
	file_name = recipe.replace(" ", "_").lower() + ".recipe"
	abspath_name = RECIPE_DATA_DIR + file_name
	if abspath_name in RECIPE_FILES:
		return abspath_name
	else:
		if not recipe.endswith(".recipe"):
			sys.exit("{}ERROR: {} is not a recipe file. Exiting..."
					 .format(color.ERROR, recipe))
		else:
			return recipe

def list_recipes(ret=False):
	"""List all recipes in the database"""
	
	recipe_list = sorted(RECIPE_NAMES)
	
	if ret:
		return recipe_list
	else:
		for item in columnify(recipe_list):
			PP.pprint(item)
		#for item in recipe_list: print(item)

def columnify(iterable):
	# First convert everything to its repr
    strings = [repr(x) for x in iterable]
    # Now pad all the strings to match the widest
    widest = max(len(x) for x in strings)
    padded = [x.ljust(widest) for x in strings]
    return padded

def md5():
	#TODO-> md5 funtion to check which yaml files have changed and then write the coresponding xml.
	pass

def improper_to_mixed(fraction):
	str_frac = str(fraction)
	x = str_frac.split('/')
	num = int(x[0])
	den = int(x[1])
	whole_part = num // den
	fract_part = num % den
	return "{} {}/{}".format(whole_part, fract_part, den)

class IngredientIterator:
	
	def __init__(self, iterable):
		self.ingredients = iterable
		pass

	def __iter__(self):
		pass

	def __next__(self):
		pass
		raise StopIteration


