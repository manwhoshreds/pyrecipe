"""
    utils for the pyrecipe program

"""
import os
import sys
import string
import textwrap

import pyrecipe.config as config
from .format import color

def mins_to_hours(mins):
    #days = mins // 1440
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
        wrapped_str = str(index) + ". ", wrap
        wrapped.append(wrapped_str)
    return wrapped

def check_source(source):
    if os.path.isdir(source):
        return sys.exit(msg('{} is a directory'
                        .format(source), 'ERROR'))
    elif os.path.isfile(source):
        if not source.endswith('.recipe'):
            return sys.exit(msg("ERROR: Pyrecipe can only read "
                            "files with a .recipe extention",
                            'ERROR'))
        else:
            return source
    # must be a string name a recipe that exist in the data dir
    else:
        file_name = get_file_name(source)
        abspath_name = os.path.join(config.RECIPE_DATA_DIR, file_name)
        try:
            assert open(abspath_name)
            return abspath_name
        except FileNotFoundError:
            return sys.exit(msg("ERROR: {} does not exist."
                            .format(file_name), 'ERROR'))
    
def get_file_name(source, ext='recipe'):
    strip_punc = ''.join(c for c in source if c not in string.punctuation)
    file_name = strip_punc.replace(" ", "_").lower()
    file_name = '{}.{}'.format(file_name, ext)
    return file_name



    # First convert everything to its repr
    strings = [repr(x) for x in iterable]
    # Now pad all the strings to match the widest
    widest = max(len(x) for x in strings)
    padded = [x.ljust(widest) for x in strings]
    return padded

def stats(verb=0):
    """Print statistics about your recipe database and exit."""
    
    version()
    print("Recipes: {}".format(len(RECIPE_DATA_FILES)))
    if verb >= 1:
        print("Recipe data directory: {}".format(RECIPE_DATA_DIR))
        print("Recipe xml directory: {}".format(RECIPE_XML_DIR))
        print("Default random recipe: {}".format(RAND_RECIPE_COUNT))

def msg(text, level='INFORM'):
    msg_level = {'INFORM': 'cyan',
                 'ERROR': 'red',
                 'WARN': 'yellow'}
    return color(text, msg_level[level])

# testing
if __name__ == '__main__':
    #sys.exit(msg('hello', 'WARN'))
    import random
    text = 'ok so what'
    def colorify(text):
        rand = random.randint(1,3)
        if rand == 1:
            colo = color.INFORM
        elif rand == 2:
            colo = color.WARN
        elif rand == 3:
            colo = color.ERROR 
        
        return(colo + text + color.NORMAL)
    color = [colorify(x) for x in text]
    print(''.join(x for x in color))

