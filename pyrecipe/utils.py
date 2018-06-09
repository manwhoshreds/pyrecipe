"""
    utils for the pyrecipe program

"""
import os
import sys
import string
import textwrap

import lxml.etree as ET
from termcolor import colored

from pyrecipe import config, db

S_DIV = lambda m: colored('~' * m, 'white')

class RecipeNotFound(Exception):
    pass

def format_text(string):
    """Format text for use in pyrecipe function.
    
    Formats the text so that it is more consistant and
    can be used throughout pyrecipe. Text is striped of 
    extraneous whitepace and lower cased. This function
    is mainly used when string input is recieved from the user.
    """
    return string.lower().strip()

def mins_to_hours(mins):
    """Convert minutes to hours."""
    #days = mins // 1440
    hours = mins // 60
    minutes = mins - hours * 60
    if not hours:
        return "{} m".format(mins)
    else:
        converted_time = "%d h %02d m" % (hours, minutes)
    return converted_time

def wrap(str_list, width=79):
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
        wrapp = wrapper.fill(step)
        wrapped_str = str(index) + ". ", wrapp
        wrapped.append(wrapped_str)
    return wrapped

def get_source_path(source):
    """Closer inspection of the source.

    If all is well, the function returns the source path.
    """
    source = source.replace("_", " ")
    if os.path.isdir(source):
        sys.exit(msg("{} is a directory.".format(source), "ERROR"))
    elif os.path.isfile(source):
        if not source.endswith('.recipe'):
            sys.exit(msg("Pyrecipe can only read files with a "
                         ".recipe extention.", "ERROR"))
        else:
            return source
    else:
        # We must have asked for the recipe using only its name
        # after all, this is the intended way to lookup the recipe.
        file_name = get_file_name(source)
        if file_name is None:
            sys.exit(msg("{} does not exist in the database."
                         .format(source), "ERROR"))
        else:
            return file_name

def get_file_name(source):
    """Get the file name for a recipe source that is in the database.
    
    The file names given to the recipes are derrived from the uuid associated
    with the recipe. This function looks up and returns the uuid from the
    database.
    """
    recipe_uuid = db.get_data()['uuids'].get(source, None)
    if recipe_uuid is None:
        return None
    file_name = get_file_name_from_uuid(recipe_uuid)
    return file_name

def get_file_name_from_uuid(uuid):
    """Return a file name using the recipes uuid."""
    file_name = uuid.replace('-', '') + ".recipe"
    file_name = os.path.join(config.RECIPE_DATA_DIR, file_name)
    return file_name

def strip_punctuation(phrase):
    """Returns a phrase without punctuation."""
    phrase = ''.join(c for c in phrase if c not in string.punctuation)
    return phrase

def get_file_name_from_recipe(recipe_name, file_extention='recipe'):
    """Return a file name using the name of the recipe."""
    recipe_name = strip_punctuation(recipe_name)
    recipe_name = recipe_name.replace(' ', '_')
    file_name = '{}.{}'.format(recipe_name, file_extention)
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
    if level == 'FATAL':
        text = '{} {}'.format(colored('ERROR:', on_color='on_red'),
                              colored(text, 'white'))
        return sys.exit(text)
    
    elif level == 'INFORM':
        text = colored(text, 'cyan', attrs=['bold'])
        return text
    
    elif level == 'WARN':
        text = colored(text, 'yellow', attrs=['bold'])
        return text

def recipe2xml(func):
    """Get the xml representation of a recipe."""
    def get_xml_string(xml_root):
        result = ET.tostring(
            xml_root,
            xml_declaration=True,
            encoding='utf-8',
            with_tail=False,
            method='xml',
            pretty_print=True
        )
        return result.decode('utf-8')


    def wrapper(recipe):
        root_keys = list(recipe._recipe_data.keys())
        
        xml_root = ET.Element('recipe')
        xml_root.set('name', recipe['recipe_name'])

        # Not interested in adding notes to xml, maybe in the future
        for item in root_keys:
            if item not in ('ingredients', 'alt_ingredients', 'notes',
                            'steps', 'recipe_name', 'category'):
                xml_entry = ET.SubElement(xml_root, item)
                xml_entry.text = str(recipe[item])

        # ready_in
        # not actually an ord tag, so is not read from recipe file
        # it is simply calculated within the class
        #if recipe['prep_time'] and recipe['cook_time']:
        #    recipe['ready_in'] = RecipeNum(
        #        self['prep_time']) + RecipeNum(self['cook_time']
        #    )
        #elif self['prep_time'] and self['bake_time']:
        #    self['ready_in'] = RecipeNum(
        #        self['prep_time']) + RecipeNum(self['bake_time']
        #    )
        #else:
        #    self['ready_in'] = self['prep_time']

        # oven_temp
        #if recipe['oven_temp']:
        #    recipe.oven_temp = self['oven_temp']
        #    recipe.ot_amount = self['oven_temp']['amount']
        #    self.ot_unit = self['oven_temp']['unit']
        #    xml_oven_temp = ET.SubElement(self.xml_root, "oven_temp")
        #    xml_oven_temp.text = str(self.ot_amount) + " " + str(self.ot_unit)

        ingredients, alt_ingredients = recipe.get_ingredients()
        
        # ingredients
        if ingredients:
            xml_ingredients = ET.SubElement(xml_root, "ingredients")
            for ingred in ingredients:
                xml_ingred = ET.SubElement(xml_ingredients, "ingred")
                xml_ingred.text = ingred

        # alt_ingredients 
        if alt_ingredients:
            for item in alt_ingredients:
                xml_alt_ingredients = ET.SubElement(xml_root, "alt_ingredients")
                xml_alt_ingredients.set('alt_name', item)
                for ingred in alt_ingredients[item]:
                    xml_alt_ingred = ET.SubElement(xml_alt_ingredients, "ingred")
                    xml_alt_ingred.text = ingred

        xml_steps = ET.SubElement(xml_root, "steps")
        for step in recipe['steps']:
            steps_of = ET.SubElement(xml_steps, "step")
            steps_of.text = step['step']
        
        return get_xml_string(xml_root)
    
    return wrapper


if __name__ == '__main__':
    r = Recipe('pesto')
    test = get_recipe_xml(r)
    print(test)
