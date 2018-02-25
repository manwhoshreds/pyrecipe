"""
	pyrecipe.argfuncts
"""

import sys
import subprocess
import shutil
import os
from zipfile import ZipFile

from .config import PP, EDITOR, RECIPE_DATA_FILES
from pyrecipe import utils, shopper, manifest, color
from pyrecipe.recipe import Recipe, RecipeWebScraper
import pyrecipe.gui.maingui as gui
from pyrecipe.console_gui.edit_recipe import RecipeEditor

def dump_data(args):
    r = Recipe(args.source)
    r.dump_to_screen(args.data_type)

def start_gui():
    gui.start()

def print_shopping_list(args):
	
    if args.random:
        rr = shopper.RandomShoppingList(args.random)
        rr.print_random()
    else:
        menu_items = args.recipes	
        if len(menu_items) == 0:
            sys.exit('You must supply at least one recipe'
                     ' to build your shopping list from!')
            
        sl = shopper.ShoppingList()
        for item in menu_items:
            sl.update(item)
        if args.write:			
            sl.print_list(write=True)
        else:
            sl.print_list()

def fetch_recipe(args):
    scraper = RecipeWebScraper(args.url)
    scraper.print_recipe()
    #RecipeEditor(scraper, add=True).start()

def print_recipe(args):
    r = Recipe(args.source)
    r.print_recipe(verb_level=0)


def show_stats(args):
    utils.stats(args.verbose)

def delete_recipe(args):
    source = args.source
    r = Recipe(source) 
    file_name = r['source']
    answer = input("Are you sure your want to delete {}? yes/no ".format(source))
    if answer.strip() == 'yes':
        os.remove(file_name)
        print("{} has been deleted".format(source))
    else:
        print("{} not deleted".format(source))

def edit_recipe(args):
    RecipeEditor(args.source).start()

def add_recipe(args):
    name = utils.get_file_name(args.name)
    if name in RECIPE_DATA_FILES:
        sys.exit('{}ERROR: A recipe with that name already exist.'.format(color.ERROR))
    else:
        RecipeEditor(args.name, add=True).start()

def print_list(args):
    recipes = manifest.recipe_names
    lower_recipes = [x.lower() for x in recipes]
    for item in sorted(lower_recipes):
        print(item.title())
	
def version(args):
    print(utils.version())

def export_recipes(args):
    try:
        output_dir = os.path.realpath(args.output_dir)
        os.makedirs(output_dir)
    except FileExistsError:
        sys.exit('{}ERROR: A directory with name {} already exists.'
                 .format(color.ERROR, output_dir))
    except TypeError:
        output_dir = os.getcwd()
        
    recipe_name = args.source
    r = Recipe(args.source)
    xml = r.xml_data
    file_name = utils.get_file_name(args.source, 'xml')
    file_name = os.path.join(output_dir, file_name)
    if args.xml:
        print("{}Writing to file: {}{}".format(color.INFORM, file_name, color.NORMAL))
        with open(file_name, "w") as file:
                file.write(str(xml))
    if args.recipe:
        src = r.source
        dst = os.path.join(output_dir, r.file_name)
        if os.path.isfile(dst):
            sys.exit('{}ERROR: File already exists.'
                    .format(color.ERROR))
        else:
            shutil.copyfile(src, dst)


