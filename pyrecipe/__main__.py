#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
# PYTHON_ARGCOMPLETE_OK
"""
    recipe_tool
    pyrecipe.argfuncs
    ~~~~~~~~~~~
    
    recipe_tool is the frontend commandline interface to
    the pyrecipe library.
    We must first build the database before moving on
    also if one wishes to rebuild the database for whatever reason,
    simply delete the db file and run the recipe_tool to rebuild
"""
import os
import sys
import shutil
import argparse

import argcomplete

import pyrecipe.utils as utils
import pyrecipe.shopper as shopper
from pyrecipe import (Recipe, RecipeWebScraper, SCRAPEABLE_SITES, 
                      version_info, config, spell_check, __scriptname__)
import pyrecipe.db as DB
from pyrecipe.console_gui import RecipeEditor, RecipeMaker

## Start command functions

def cmd_print(args):
    """Print a recipe to stdout."""
    recipe = Recipe(args.source, verbose=args.verbose)
    print(recipe)

def cmd_edit(args):
    """Edit a recipe using the urwid console interface (ncurses)."""
    r = Recipe(args.source)
    RecipeEditor(r).start()

def cmd_add(args):
    """Add a recipe to the recipe store."""
    name = utils.get_file_name(args.name)
    if name in config.RECIPE_DATA_FILES:
        sys.exit(
            utils.msg('A recipe with that name already'
                      ' exist in the database.', 'ERROR')
        )
    else:
        name = args.name.strip()
        RecipeEditor(name, add=True).start()

@DB.delete_recipe
def cmd_remove(args):
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

def cmd_make(args):
    """Make a recipe using the urwid automated script.
    
    This script helps you make your recipe by cycling through
    ingredients and steps. It also hands a hands free voice
    recognition feature in case your hands are stuck in flour
    or other ingredients. Who knows, your cooking!!
    """
    RecipeMaker(args.source).start()

def cmd_search(args):
    """Search the recipe database."""
    search = args.search
    check = spell_check(args.search)
    if check != args.search:
        print("Nothing found. Showing results for \"{}\" instead.".format(check))
        search = check
    
    db = DB.RecipeDB()
    results = db.search(search)
    numres = len(results)
    if numres == 0:
        sys.exit(
            "Your search for \"{}\" produced no results".format(args.search))
    results = "\n".join(results)
    print(results)

def cmd_shop(args):
    """Print a shopping list."""
    if args.random:
        rr = shopper.RandomShoppingList(args.random)
        rr.print_random(write=args.save)
    else:
        menu_items = args.recipes	
        if len(menu_items) == 0:
            sys.exit('You must supply at least one recipe'
                     ' to build your shopping list from!')
            
        sl = shopper.ShoppingList()
        for item in menu_items:
            sl.update(item)
        sl.print_list(write=args.save)

def cmd_dump(args):
    """Dump recipe data in 1 of three formats."""
    r = Recipe(args.source)
    r.dump_to_screen(args.data_type)

def cmd_export(args):
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

def cmd_show(args):
    """Show the statistics information of the recipe database."""
    utils.stats(args.verbose)

def cmd_fetch(args):
    """Fetch a recipe from a web source."""
    if args.list_sites:
        sys.exit(print('\n'.join(SCRAPEABLE_SITES)))
    
    scraper = RecipeWebScraper(args.url)
    print('Looking up recipe now...')
    scraper.scrape()
    if args.edit:
        RecipeEditor(scraper).start()
    else:
        scraper.print_recipe()

def version():
    """Print pyrecipe version information."""
    sys.exit(version_info())

## End command funtions

def recipe_completer(**kwargs):
    """List of recipes for completer."""
    data = DB.get_data()
    recipe_names = data['recipe_names']
    return recipe_names

def build_recipe_database():
    """Build the recipe database."""
    database = db.RecipeDB()
    database.create_database()
    for item in config.RECIPE_DATA_FILES:
        r = Recipe(item)
        database.add_recipe(r)

def parse_args():
    """Parse args for recipe_tool."""
    parser = argparse.ArgumentParser(
        description="Recipe_tool has tab completion functionality. \
                     After adding a recipe, simply run recipe_tool \
                     print <TAB><TAB> to view whats available.",
        add_help=False
    )
    parser.add_argument(
        "-h", "--help",
        action='help',
        help='Show this help message and quit'
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase the verbosity of output. \
              Only works with print and show subcommands."
    )
    parser.add_argument(
        "-V",
        "--version",
        dest="version",
        action="store_true",
        help="Print version and exit"
    )
    # <-- Subparsers start here -->
    subparser = parser.add_subparsers(dest='subparser')

    # recipe_tool print
    parser_print = subparser.add_parser(
        "print", 
        help="Print the recipe to screen"
    )
    parser_print.add_argument(
        "source", 
        help="Recipe to print"
    ).completer = recipe_completer

    parser_print.add_argument(
        "--yield",
        default=0,
        nargs='?',
        metavar='AMOUNT',
        type=int,
        dest="yield_amount",
        help="Specify a yield for the recipe."
    ).completer = recipe_completer
    
    # recipe_tool edit
    parser_edit = subparser.add_parser(
        "edit", 
        help="Edit a recipe data file"
    )
    parser_edit.add_argument(
        "source", 
        type=str, 
        help="Recipe to edit"
    ).completer = recipe_completer

    # recipe_tool add
    parser_add = subparser.add_parser("add", help='Add a recipe')
    parser_add.add_argument("name", help='Name of the recipe to add')
    
    # recipe_tool remove
    parser_remove = subparser.add_parser("remove", help='Delete a recipe')
    parser_remove.add_argument(
        "source", 
        help='Recipe to delete'
    ).completer = recipe_completer
    
    # recipe_tool make
    parser_make = subparser.add_parser(
        "make", 
        help='Make a recipe using the urwid automated script'
    )
    parser_make.add_argument(
        "source", 
        help='Recipe to make'
    ).completer = recipe_completer
    
    # recipe_tool search
    parser_search = subparser.add_parser(
        "search", 
        help='Search the recipe database'
    )
    parser_search.add_argument(
        "search",
        help='Search the recipe database'
    )
    # recipe_tool shop
    parser_shop = subparser.add_parser("shop", help='Make a shopping list')
    parser_shop.add_argument(
        "recipes",
        nargs="*",
        help='List of recipe to compile shopping list'
    ).completer = recipe_completer
    
    parser_shop.add_argument(
        "-a",
        "--add",
        nargs='?',
        type=str,
        help="Add an ingredient or a list of ingredients to the current "
             "shopping list."
    )
    parser_shop.add_argument(
        "-c",
        "--commit",
        action="store_true",
        help="Commit the current shopping list to a remote server."
    )
    parser_shop.add_argument(
        "-p",
        "--print-list",
        action="store_true",
        help="Print the current shopping list."
    )
    parser_shop.add_argument(
        "-r",
        "--random",
        nargs='?',
        const=config.RAND_RECIPE_COUNT,
        type=int,
        metavar="NUM",
        dest="random",
        help="Pick n random recipes for the week"
    )
    parser_shop.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="Save the current shopping list."
    )
    # recipe_tool dump
    parser_dump = subparser.add_parser(
        "dump",
        help="Dump yaml or xml representation of recipe stdout"
    )
    parser_dump.add_argument(
        "source",
        help="Recipe to dump data from"
    ).completer = recipe_completer
    
    parser_dump.add_argument(
        "-x",
        "--xml",
        dest="data_type",
        action="store_const",
        const="xml",
        help="Dump sorce xml tree to standard output"
    )
    parser_dump.add_argument(
        "-y",
        "--yaml",
        dest="data_type",
        action="store_const",
        const="yaml",
        help="Dump source yaml to standard output"
    )
    parser_dump.add_argument(
        "-r",
        "--raw",
        dest="data_type",
        action="store_const",
        const="raw",
        help="Dump source data in its raw format"
    )
    # recipe_tool export
    parser_export = subparser.add_parser(
        "export",
        help="Export recipes in xml format"
    )
    parser_export.add_argument(
        "source",
        help="Sorce file to export"
    ).completer = recipe_completer
    
    parser_export.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        type=str,
        nargs="?",
        help="Choose a directory to output file"
    )
    parser_export.add_argument(
        "-a",
        "--all",
        help="Export all files in the database"
    )
    parser_export.add_argument(
        "-x",
        "--xml",
        dest="xml",
        action='store_true',
        help="Export file in xml format"
    )
    parser_export.add_argument(
        "-r",
        "--recipe",
        dest="recipe",
        action='store_true',
        help="Export recipe file"
    )
    # recipe_tool show
    parser_show = subparser.add_parser(
        "show",
        help="Show statistic from the reicpe database"
    )
    # recipe_tool fetch
    parser_fetch = subparser.add_parser(
        "fetch",
        help="Fetch a recipe from a website. \
              (currently only supports tasty.co, more to come)"
    )
    parser_fetch.add_argument(
        "url",
        nargs="?",
        default=None,
        help="Url of a recipe to fetch"
    )
    parser_fetch.add_argument(
        "-e",
        "--edit",
        action="store_true",
        help="Open the recipe in the editor. Select this to save the recipe"
    )
    parser_fetch.add_argument(
        "--list-sites",
        action="store_true",
        help="List the sites that {} can download from".format(__scriptname__)
    )
    parser_fetch.add_argument(
        "--search",
        help="Search the web for a recipe to scrape"
    )

    # auto completion
    argcomplete.autocomplete(parser)
    
    args = parser.parse_args()
    import sys
    if len(sys.argv) == 1:
        sys.exit(parser.print_help())
    elif len(sys.argv) == 2 and args.verbose:
        # if recipe_tool is invoked with only a 
        # verbose flag it causes an exception so 
        # here we offer help if no other flags are given
        sys.exit(parser.print_help())
    else:
        return args

def main():
    """Main entry point of recipe_tool."""
    # Build the databse first if it does not exist.
    # Useful for rebuilding db. Just delete the db file.
    db_exists = os.path.exists(config.DB_FILE)
    recipe_exists = len(config.RECIPE_DATA_FILES) > 0
    if not db_exists and recipe_exists:
        print('Building recipe database...')
        build_recipe_database()
    
    # Now parse the args
    args = parse_args()
    case = {
        'print': cmd_print,
        'edit': cmd_edit,
        'add': cmd_add,
        'remove': cmd_remove,
        'make': cmd_make,
        'search': cmd_search,
        'shop': cmd_shop,
        'dump': cmd_dump,
        'export': cmd_export,
        'show': cmd_show,
        'fetch': cmd_fetch,
    }
    if args.version:
        version()
    else:
        case[args.subparser](args)

if __name__ == '__main__':
    sys.exit(main())
