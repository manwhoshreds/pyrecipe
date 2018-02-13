"""
	utils for the pyrecipe program

"""
import os
import sys
import subprocess
import string
import textwrap
from fractions import Fraction
from numbers import Number

from pyrecipe.config import (__version__, __scriptname__, __email__,
                             RECIPE_DATA_DIR, RECIPE_DATA_FILES,
                             DISH_TYPES, VIM_MODE_LINE, EDITOR)
from pyrecipe import yaml, p, color, manifest


def mins_to_hours(mins):
    days = mins // 1440
    hours = mins // 60
    minutes = mins - hours * 60
    if not hours:
        return "{} m".format(mins)
    else:
        len = "%d h %02d m" % (hours, minutes)
    return len

def wrap(str_list, width=60):
    if not isinstance(str_list, list):
        raise TypeError('First argument must be a list.')
    wrapped = []
    wrapper = textwrap.TextWrapper(width)
    wrapper.subsequent_indent = '   '
    if len(str_list) > 9:
        wrapper.initial_indent = ' '
        wrapper.subsequent_indent = '    '

    for index, step in enumerate(str_list, start=1):
        if index >= 10:
            wrapper.initial_indent = ''
        wrap = wrapper.fill(step)
        wrapped_str = str(index) + ".", wrap
        wrapped.append(wrapped_str)
    return wrapped

def check_source(source):
    if os.path.isdir(source):
        return sys.exit('{}ERROR: {} is a directory'
                        .format(color.ERROR, source))
    elif os.path.isfile(source):
        if not source.endswith('.recipe'):
            return sys.exit("{}ERROR: Pyrecipe can only read "
                            "files with a .recipe extention"
                            .format(color.ERROR))
        else:
            return source
    # must be a string name a recipe that exist in the data dir
    else:
        file_name = get_file_name(source)
        abspath_name = os.path.join(RECIPE_DATA_DIR, file_name)
        try:
            assert open(abspath_name)
            return abspath_name
        except FileNotFoundError:
            return sys.exit("{}ERROR: {} does not exist."
                            .format(color.ERROR, abspath_name))
    
def get_file_name(source, ext='recipe'):
    strip_punc = ''.join(c for c in source if c not in string.punctuation)
    file_name = strip_punc.replace(" ", "_").lower()
    file_name = '{}.{}'.format(file_name, ext)
    return file_name

def list_recipes(ret=False):
    """List all recipes in the database"""
    
    recipe_list = manifest.recipe_names
    if ret:
        return recipe_list
    else:
        for item in columnify(recipe_list):
            PP.pprint(item)
        for item in recipe_list: print(item)

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
        file_name = get_source_path(recipe_name)
        if os.path.isfile(file_name):
            sys.exit("File with this name already exist in directory exiting...")
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
        temp_yaml = yaml.load(template)
        print("Writing to file... " + file_name)
        with open(file_name, "w") as file:
            yaml.dump(temp_yaml, file)
    
    except KeyboardInterrupt:
        sys.exit("\nExiting...")
    
    subprocess.call([EDITOR, file_name])

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

# testing
if __name__ == '__main__':
    test = 'i am a super, dup-awsome.*&^%'
    ok = get_source_path(test)
    print(ok)


