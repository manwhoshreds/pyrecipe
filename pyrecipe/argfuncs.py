"""
	pyrecipe.argfuncts
"""

#import os
import sys
import subprocess
import os
from .config import PP
from .utils import *

import pyrecipe.recipe as recipe
import pyrecipe.maingui as gui

def dump_data(args):
	
    r = recipe.Recipe(args.source)

    if args.print_yaml:
        PP.pprint(r.recipe_data)
        exit(0)
    if args.print_xml:
        print(r.xml_data)
        exit(0)
	
def start_gui():
	
    gui.start()

def print_shopping_list(args):
	
    if args.random:
        rr = recipe.RandomShoppingList(args.random)
        rr.print_random()
    else:
        menu_items = args.recipes	
        if len(menu_items) == 0:
            sys.exit('You must supply at least one recipe'
                     ' to build your shopping list from!')
            
        sl = recipe.ShoppingList()
        for item in menu_items:
            sl.update(item)
        if args.write:			
            sl.print_list(write=True)
        else:
            sl.print_list()

def check_file(args):
    if args.source == "all":
        for item in recipe.RECIPE_NAMES:
            r = recipe.Recipe(item)
            r.check_file()
    else:
        r = recipe.Recipe(args.source)
        r.check_file()
	



def print_recipe(args):
    r = recipe.Recipe(args.source)
    r.print_recipe(args.verbose)

def show_stats(args):
    recipe.stats(args.verbose)

def delete_recipe(args):
    import os
    source = args.source
    file_name = str(recipe.Recipe(source))
    answer = input("Are you sure your want to delete {}? yes/no ".format(source))
    if answer.strip() == 'yes':
        os.remove(file_name)
    else:
        print("{} not deleted".format(source))

def edit_recipe(args):
    source = get_file_name(args.source)
    subprocess.call([recipe.EDITOR, source])

def add_recipe(args):
    if args.name.title() in recipe.list_recipes(ret=True):
        sys.exit('A recipe with that name already exist in the recipe store')
    else:
        recipe.template(args.name)


def print_list(args):
	
    recipe.list_recipes()

def version(args):
	
    print(recipe.version())

def export_recipes(args):
	
    recipe_name = args.source
    r = recipe.Recipe(args.source)
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
