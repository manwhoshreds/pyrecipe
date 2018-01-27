"""
	pyrecipe.argfuncts
"""

import sys
import subprocess
import os

from .config import PP, EDITOR
from pyrecipe import utils, shopper, manifest
from pyrecipe.recipe import Recipe, RecipeWebScraper
import pyrecipe.gui.maingui as gui

def dump_data(args):
	
    r = Recipe(args.source)

    if args.print_yaml:
        r.dump_yaml()
        sys.exit(0)
    if args.print_xml:
        r.dump_xml()
        sys.exit(0)
    if args.print_raw:
        PP.pprint(r.recipe_data) 
        sys.exit(0)
	
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

def check_file(args):
    if args.source == "all":
        for item in recipe.RECIPE_NAMES:
            r = Recipe(item)
            r.check_file()
    else:
        r = Recipe(args.source)
        r.check_file()
	
def fetch_recipe(args):
    scraper = RecipeWebScraper(args.url)
    if args.save:
        scraper.dump()
    else:
        scraper.print_recipe(verb_level=2)

def print_recipe(args):
    r = Recipe(args.source)
    r.print_recipe(args.verbose)

def show_stats(args):
    utils.stats(args.verbose)

def delete_recipe(args):
    source = args.source
    r = Recipe(source) 
    file_name = r['source']
    answer = input("Are you sure your want to delete {}? yes/no ".format(source))
    if answer.strip() == 'yes':
        os.remove(file_name)
    else:
        print("{} not deleted".format(source))

def edit_recipe(args):
    source = utils.get_file_name(args.source)
    subprocess.call([EDITOR, source])

def add_recipe(args):
    if args.name.title() in utils.list_recipes(ret=True):
        sys.exit('A recipe with that name already exist in the recipe store')
    else:
        utils.template(args.name)


def print_list(args):
    recipes = manifest.recipe_names
    lower_recipes = [x.lower() for x in recipes]
    for item in sorted(lower_recipes):
        print(item.title())
	
def version(args):
	
    print(utils.version())

def export_recipes(args):
	
    recipe_name = args.source
    r = Recipe(args.source)
    xml = r.xml_data
    new_name = recipe_name.replace(" ", "_")
    lower_new_name  = new_name.lower() + ".xml"# I prefer file names to be all lower case
    # check for output dir flag	and make dir if it does not exist
    if args.output_dir:	
        output_dir = os.path.abspath(args.output_dir)
        if os.path.exists(output_dir):
            if not os.path.isdir(output_dir):
                print("Not a directory")
                exit(1)
        else:
            try:
                os.makedirs(output_dir)
            except OSError:
                print("couldnt create directory")
                exit(1)
    else:
        output_dir = RECIPE_XML_DIR
    
    file_name = os.path.join(output_dir, lower_new_name)	
            
    print("{}Writing to file: {}{}".format(color.INFORM, file_name, color.NORMAL))
    with open(file_name, "w") as file:
            file.write(str(xml))
