"""
	utils for the pyrecipe program

"""
import os
import sys
from fractions import Fraction

import inflect


from .config import (__version__, __scriptname__, __email__,
                     RECIPE_DATA_DIR, RECIPE_DATA_FILES)


# Inflects default behaviour for returning the singular of a word is
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

    def plural(self, word, count=None):
        if count: 
            if count <= 1:
                return word
            else:
                word = super().plural(word)
                return word
        else:
            word = super().plural(word)
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
    #if isinstance(n, str):
    if len(n.split('⁄')) == 2:
        n = '/'.join(n.split('⁄'))
        return float(Fraction(n))
    
        #float(sum(Fraction(s) for s in n.split()))
    else: 
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
        sys.exit('{} does not exist in the recipe directory.'.format(abspath_name))


#def list_recipes(ret=False):
#    """List all recipes in the database"""
    
    #recipe_list = sorted(RECIPE_NAMES)
    
#    if ret:
#        return recipe_list
#    else:
#        for item in columnify(recipe_list):
#            PP.pprint(item)
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

def template(recipe_name):
    """Start the interactive template builder"""
    
    try:
        print("Interactive Template Builder. Press Ctrl-c to abort.\n")
        template = ""
        template += "recipe_name: {}\n".format(recipe_name)
        # check if file exist, lets catch this early so we 
        # can exit before entering in all the info
        file_name = utils.get_file_name(recipe_name)
        if os.path.isfile(file_name):
            print("File with this name already exist in directory exiting...")
            exit(1)
        while True:
            dish_type = input("Enter dish type: ")
            if dish_type not in DISH_TYPES:
                print("Dish type must be one of {}".format(", ".join(DISH_TYPES)))
                continue
            else:
                break
        template += "dish_type: {}\n".format(dish_type)
        prep_time = input("Enter prep time: ")
        template += "prep_time: {}\n".format(prep_time)
        cook_time = input("Enter cook time (optional): ")
        if cook_time:
            template += "cook_time: {}\n".format(cook_time)
        author = input("Enter authors full name: ")
        template += "author: {}\n".format(author)
        ingred_amount = 0
        while True:
            try:
                ingred_amount = int(input("Enter amount of ingredients: "))
            except ValueError:
                print("Input must be a number")
                continue
            else:
                break
        template += "ingredients:\n"
        for item in range(ingred_amount):
            template += "    - name:\n      amounts:\n        - amount:\n          unit:\n"
        template += "steps:\n  - step: Coming soon"
        template += VIM_MODE_LINE
        print("Writing to file... " + file_name)
        temp_yaml = yaml.load(template)
        test = yaml.dump(temp_yaml)
        print(test)
        
        #with open(file_name, "w") as tmp:
        #    tmp.write(str(template))
    
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    
    #subprocess.call([EDITOR, file_name])

def check_file(soruce, silent=False):
    """function to validate Open Recipe Format files"""
    
    failure_keys = []
    failure_units = []
    failure_prep_types = []
    # amounts must be numbers
    failure_amounts = []
    failed = False
    
    for item in self.ingredient_data:
        try:	
            amount = item['amounts'][0].get('amount', None)
            if isinstance(amount, Number):
                pass
            else:
                failure_amounts.append(item['name'])
                failed = True
        except KeyError:
            continue

    for item in REQUIRED_ORD_KEYS:
        if item not in self.mainkeys:
            failure_keys.append(item)
            failed = True
    
    for item in self.ingredient_data:
        try:
            unit = item['amounts'][0]['unit']
            if unit not in INGRED_UNITS:
                failure_units.append(unit)
                failed = True
        except KeyError:
            continue
    
    for item in self.ingredient_data:
        try:
            prep = item['prep']
            if prep not in PREP_TYPES and prep not in failure_prep_types:
                failure_prep_types.append(prep)
                failed = True
        except KeyError:
            continue
    
    if failed:
        if silent:
            return True
        else:
            if len(failure_keys) > 0:
                print(color.ERROR 
                    + self.source
                    + ": The following keys are required by the ORD spec: " 
                    + ",".join(failure_keys) 
                    + color.NORMAL)
            
            if len(failure_units) > 0:
                print(color.ERROR 
                    + self.source
                    + ": The following units are not allowed by the ORD spec: " 
                    + ", ".join(failure_units)
                    + color.NORMAL)
            
            if len(failure_amounts) > 0:
                print(color.ERROR 
                    + self.source
                    + ": The following ingredients have no integer amounts: " 
                    + ", ".join(failure_amounts) 
                    + color.NORMAL)
            
            if len (failure_prep_types) > 0:
                print(color.ERROR 
                    + self.source
                    + ": The following prep types are not allowed by the ORD spec: " 
                    + ", ".join(failure_prep_types) 
                    + color.NORMAL)
            
            if _recipe_data['dish_type'] not in DISH_TYPES:
                print(color.ERROR 
                    + self.source
                    + ": The current dish type is not in the ORD spec: " 
                    + _recipe_data['dish_type'] 
                    + color.NORMAL)
            
            if len(self.steps) < 1:
                print(color.ERROR 
                    + self.source
                    + ": You must at least supply one step in the recipe." 
                    + color.NORMAL)
    else:	
        if silent:
            return False
        else:
            print(color.TITLE 
                + self.source
                + " is a valid ORD file")

def version(text_only=False):
    """Print the current version of pyrecipe and exit."""
    if text_only:
        ver_str = ''
        ver_str += "{} v{}".format(__scriptname__, __version__)
        ver_str += "\nThe recipe management program."
        ver_str += "\n"
        ver_str += "\nFor any questions, contact me at {}".format(__email__)
        ver_str += "\nor type recipe_tool --help for more info."
        ver_str += "\n"
        ver_str += "\nThis program may be freely redistributed under"
        ver_str += "\nthe terms of the GNU General Public License."
        return ver_str
    else:
        ver_str = ''
        ver_str +=   "                _              _              _   {} v{}".format(__scriptname__, __version__)
        ver_str += "\n               (_)            | |            | |  The recipe management program."
        ver_str += "\n  _ __ ___  ___ _ _ __   ___  | |_ ___   ___ | |"
        ver_str += "\n | '__/ _ \/ __| | '_ \ / _ \ | __/ _ \ / _ \| |  For any questions, contact me at {}".format(__email__)
        ver_str += "\n | | |  __/ (__| | |_) |  __/ | || (_) | (_) | |  or type recipe_tool --help for more info."
        ver_str += "\n |_|  \___|\___|_| .__/ \___|  \__\___/ \___/|_|"
        ver_str += "\n                 | |                              This program may be freely redistributed under"
        ver_str += "\n                 |_|                              the terms of the GNU General Public License."
        return ver_str

def stats(verb=0):
    """Print statistics about your recipe database and exit."""
    
    version()
    print("Recipes: {}".format(len(RECIPE_DATA_FILES)))
    if verb >= 1:
        print("Recipe data directory: {}".format(RECIPE_DATA_DIR))
        print("Recipe xml directory: {}".format(RECIPE_XML_DIR))
        print("Default random recipe: {}".format(RAND_RECIPE_COUNT))
