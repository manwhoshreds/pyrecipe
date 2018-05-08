"""
	pyrecipe.argfuncs
    ~~~~~~~~~~~~~~~~~
    We must first build the database before moving on
    also if one wishes to rebuild the database for whatever reason,
    simply delete the db file and run the recipe_tool to rebuild
"""

import sys
import shutil
import os

import pyrecipe.utils as utils
import pyrecipe.shopper as shopper
from pyrecipe import (Recipe, RecipeWebScraper, 
                      version_info, config)
from pyrecipe.db import delete_recipe
from pyrecipe.console_gui import RecipeEditor, RecipeMaker

def dump_data(args):
    """Dump recipe data in 1 of three formats."""
    r = Recipe(args.source)
    r.dump_to_screen(args.data_type)

def print_shopping_list(args):
    """Print a shopping list."""
    if args.random:
        rr = shopper.RandomShoppingList(args.random)
        rr.print_random(write=args.write)
    else:
        menu_items = args.recipes	
        if len(menu_items) == 0:
            sys.exit('You must supply at least one recipe'
                     ' to build your shopping list from!')
            
        sl = shopper.ShoppingList()
        for item in menu_items:
            sl.update(item)
        sl.print_list(write=args.write)

def fetch_recipe(args):
    """Fetch a recipe from a web source."""
    scraper = RecipeWebScraper(args.url)
    if args.url:
        scraper.scrape() 
        RecipeEditor(scraper).start()
        scraper.print_recipe()
    else:
        if args.search:
            results = scraper.search(args.search)
            if results:
                print(results)
            else:
                sys.exit(utils.msg(
                    "Could not find any recipes using using the "
                    "search term \"{}\".".format(args.search), "WARN")
                )
    

def print_recipe(args):
    """Print a recipe to stdout."""
    r = Recipe(args.source)
    r.print_recipe(
        verbose=args.verbose,
        amount_level=args.yield_amount
    )

def show_statistics(args):
    """Show the statistics information of the recipe database."""
    utils.stats(args.verbose)

@delete_recipe
def delete_recipe(args):
    """Delete a recipe from the recipe store."""
    source = args.source
    r = Recipe(source) 
    file_name = r['source']
    answer = input("Are you sure your want to delete {}? yes/no ".format(source))
    if answer.strip() == 'yes':
        os.remove(file_name)
        print("{} has been deleted".format(source))
        return r['recipe_uuid']
    else:
        print("{} not deleted".format(source))
        return None

def edit_recipe(args):
    """Edit a recipe using the urwid console interface (ncurses)."""
    r = Recipe(args.source)
    RecipeEditor(r).start()

def add_recipe(args):
    """Add a recipe to the recipe store."""
    name = utils.get_file_name(args.name)
    if name in config.RECIPE_DATA_FILES:
        sys.exit(
            utils.msg('A recipe with that name already'
                      ' exist in the database.', 'ERROR')
        )
    else:
        RecipeEditor(args.name, add=True).start()

def make_recipe(args):
    """Make a recipe using the urwid automated script.
    
    This script helps you make your recipe by cycling through
    ingredients and steps. It also hands a hands free voice
    recognition feature in case your hands are stuck in flour
    or other ingredients. Who knows, your cooking!!
    """
    RecipeMaker(args.source).start()

def version(args):
    """Print pyrecipe version information."""
    print(version_info())

def export_recipes(args):
    """Export recipes in xml format."""
    try:
        output_dir = os.path.realpath(args.output_dir)
        os.makedirs(output_dir)
    except FileExistsError:
        sys.exit(utils.msg("A directory with that name already exists.", 
                           "ERROR"))
    except TypeError:
        # no output dir indicated on the cmdline throws a type error we
        # can use to default to the current working directory.
        output_dir = os.getcwd()
        
    recipe_name = args.source
    r = Recipe(args.source)
    xml = r.xml_data
    file_name = utils.get_file_name_from_recipe(args.source, 'xml')
    file_name = os.path.join(output_dir, file_name)
    
    if args.xml:
        file_name = utils.get_file_name_from_recipe(args.source, 'xml')
        print(utils.msg("Writing to file: {}".format(file_name), "INFORM"))
        with open(file_name, "w") as file:
            file.write(str(xml))
    
    if args.recipe:
        file_name = utils.get_file_name_from_recipe(args.source)
        src = r.source
        dst = os.path.join(output_dir, file_name)
        if os.path.isfile(dst):
            sys.exit(utils.msg("File already exists.", "ERROR"))
        else:
            shutil.copyfile(src, dst)
