"""
    utils for the pyrecipe program

"""
import os
import sys
import uuid
import string
import textwrap

from pyrecipe import config
from pyrecipe.db import RecipeDB
from pyrecipe.color import color

def mins_to_hours(mins):
    """Convert minutes to hours."""
    days = mins // 1440
    hours = mins // 60
    minutes = mins - hours * 60
    if not hours:
        return "{} m".format(mins)
    else:
        len = "%d h %02d m" % (hours, minutes)
    return len

def wrap(str_list, width=60):
    """Textwrap for recipes."""
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
        wrapped_str = str(index) + ". ", wrap
        wrapped.append(wrapped_str)
    return wrapped

def get_source_path(source):
    """Closer inspection of the source.
    
    If all is well, the function returns the source path. 
    """
    # We got an empty string. User is using a Recipe instance
    # to build a recipe from scratch so we dont have a source yet.
    if not source:
        return source
    
    if os.path.isdir(source):
        sys.exit(msg("{} is a directory.".format(source), "ERROR"))
    elif os.path.isfile(source):
        if not source.endswith('.recipe'):
            sys.exit(msg("Pyrecipe can only read files with a"
                         " .recipe extention.", "ERROR"))
        else:
            return source
    else:
        # We must have asked for the recipe using only its name
        # after all, this is the intended way to lookup the recipe.
        file_name = get_file_name(source)
        if file_name is None:
            sys.exit(msg("{} does not seem to exist in the database."
                         .format(source), "ERROR"))
        else:
            return file_name

def get_file_name(source):
    """Get the file name for a recipe source that is in the database"""
    db = RecipeDB()
    recipe_uuid = db.query(
        "SELECT recipe_uuid FROM Recipes WHERE name = \'{}\'".format(source)
    )
    if len(recipe_uuid) == 0:
        return None
    else:
        file_name = get_file_name_from_uuid(recipe_uuid[0][0])
        return file_name

def get_file_name_from_uuid(uuid):
    file_name = uuid.replace('-', '') + ".recipe"
    file_name = os.path.join(config.RECIPE_DATA_DIR, file_name)
    return file_name

def stats(verb=0):
    """Print statistics about your recipe database and exit."""
    print("Recipes: {}".format(len(config.RECIPE_DATA_FILES)))
    if verb >= 1:
        print("Recipe data directory: {}".format(config.RECIPE_DATA_DIR))
        print("Recipe xml directory: {}".format(config.RECIPE_XML_DIR))
        print("Default random recipe: {}".format(config.RAND_RECIPE_COUNT))

def msg(text, level='INFORM'):
    """Pyrecipe message function with color."""
    if level == 'ERROR':
        text = 'ERROR: ' + text
    
    msg_level = {'INFORM': 'cyan',
                 'ERROR': 'red',
                 'WARN': 'yellow'}

    return color(text, msg_level[level])

if __name__ == '__main__':
    name = get_file_name('pesto')
    print(name)

