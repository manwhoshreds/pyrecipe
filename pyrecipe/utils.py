"""
	utils for the pyrecipe program

"""
import os

import inflect

from .config import *


# Inflects default behaviour for return the singular of words is
# not very useful to this project because it returns false if
# it comes across a non-noun word. Therfore, the following is a
# functional work-a-round
class InflectEngine(inflect.engine):

    def __init__(self):
        super().__init__()

    def singular_noun(self, word):
        singular = super().singular_noun(word)
        if singular:
            return singular
        else:
            return word

p = InflectEngine()


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
    except ValueError:
        return n

def get_file_name(source):
    file_name = source.replace(" ", "_").lower() + ".recipe"
    abspath_name = os.path.join(RECIPE_DATA_DIR, file_name)
    return abspath_name
    
def get_source_path(source):

    if not source:
        return
    if os.path.isfile(source):
        if not source.endswith(".recipe"):
            sys.exit("{}ERROR: {} is not a recipe file. Exiting..."
                     .format(color.ERROR, source))
        else:
            return source
    
    file_name = source.replace(" ", "_").lower() + ".recipe"
    abspath_name = os.path.join(RECIPE_DATA_DIR, file_name)
    if abspath_name in RECIPE_DATA_FILES:
        return abspath_name
    else:
        sys.exit('Cannot create new recipe')


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

def improper_to_mixed(fraction):
    str_frac = str(fraction)
    x = str_frac.split('/')
    num = int(x[0])
    den = int(x[1])
    whole_part = num // den
    fract_part = num % den
    return "{} {}/{}".format(whole_part, fract_part, den)

def all_singular(iterable):
    words = [p.singular_noun(x) for x in iterable]
    return words
