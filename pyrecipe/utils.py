"""
    utils for the pyrecipe program

"""
import os
import sys
import string

import lxml.etree as ET
from termcolor import colored


DISH_TYPES = "TEST"


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


def get_source_path(source):
    """Closer inspection of the source.

    If all is well, the function returns the source path.
    """
    abspath = os.path.abspath(source)
    if os.path.isdir(abspath):
        pass
        #sys.exit(msg("{} is a directory.".format(source), "ERROR"))
    elif os.path.isfile(abspath):
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
            sys.exit('recipe not found')
        else:
            return file_name

def get_file_name(source):
    """Get the file name for a recipe source that is in the database.
    
    The file names given to the recipes are derrived from the uuid associated
    with the recipe. This function looks up and returns the uuid from the
    database.
    """
    recipe_uuid = DBInfo().get_uuid(source)
    if recipe_uuid is None:
        return None
    file_name = get_file_name_from_uuid(recipe_uuid)
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


def message(message, level, recipe=None):
    """Pyrecipe message function with color."""
    case = {
        "recipe_not_found": f"{recipe} could not be found in the database",
        "recipe_deleted": f"{recipe} was deleted from the database",
        "recipe_not_deleted": f"{recipe} was not deleted from the database"
    }
    colored_message = colored(case[message], 'white')
    lvl = {
        'ERROR': colored('ERROR:', 'white', on_color='on_red'),
        'WARN': colored('WARN:', 'white', on_color='on_yellow'),
        'INFORM': colored('INFORM:', 'white', on_color='on_cyan')
    }
    text = f'{lvl[level]} {colored_message}'
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
        xml_root.set('name', recipe.name)

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

        ingreds, named = recipe.get_ingredients(fmt='string')
        
        # ingredients
        if ingreds:
            xml_ingredients = ET.SubElement(xml_root, "ingredients")
            for ingred in ingreds:
                xml_ingred = ET.SubElement(xml_ingredients, "ingred")
                xml_ingred.text = ingred

        # alt_ingredients 
        if named:
            for item in named:
                xml_alt_ingredients = ET.SubElement(xml_root, "alt_ingredients")
                xml_alt_ingredients.set('alt_name', item)
                for ingred in named[item]:
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
