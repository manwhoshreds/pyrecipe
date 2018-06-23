#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
    recipe_tool
    ~~~~~~~~~~~

    recipe_tool is the frontend commandline interface to
    the pyrecipe library.
"""
import os
import sys
import glob
import shutil
import argparse

import pyrecipe.utils as utils
import pyrecipe.config as config
import pyrecipe.shopper as shopper
from pyrecipe.recipe import Recipe
from pyrecipe.ocr import RecipeOCR
from pyrecipe.spell import spell_check
from pyrecipe.webscraper import WebScraper
from pyrecipe.db import (DBInfo, DBConn, delete_recipe)
from pyrecipe.console_gui import RecipeEditor, RecipeMaker
from pyrecipe import __scriptname__, version_info

## Start command functions
def cmd_print(args):
    """Print a recipe to stdout."""
    if args.source.startswith(('https://', 'http://')):
        recipe = WebScraper.scrape(args.source)
    else:
        recipe = Recipe(args.source, recipe_yield=args.recipe_yield)
    recipe.print_recipe(args.verbose)

def cmd_edit(args):
    """Edit a recipe using the urwid console interface."""
    if args.source.startswith(('https://', 'http://')):
        recipe = WebScraper.scrape(args.source)
    else:
        recipe = Recipe(args.source)
    RecipeEditor(recipe).start()

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

@delete_recipe
def cmd_remove(args):
    """Delete a recipe from the recipe store."""
    source = args.source
    recipe = Recipe(source)
    file_name = recipe.source
    answer = input("Are you sure your want to delete {}? yes/no ".format(source))
    if answer.strip() == 'yes':
        os.remove(file_name)
        print("{} has been deleted".format(source))
        return recipe.uuid

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
    #check = spell_check(args.search)
    #if check != args.search:
    #    print("Nothing found. Showing results for \"{}\" instead.".format(check))
    #    search = check

    database = DBInfo()
    results = database.search(search)
    numres = len(results)
    if numres == 0:
        sys.exit(utils.msg(
            "Your search for \"{}\" produced no results".format(args.search),
            "INFORM")
        )
    results = "\n".join(s.lower() for s in results)
    print(results)

def cmd_shop(args):
    """Print a shopping list."""
    shoplist = shopper.ShoppingList()
    if args.print_list:
        shoplist.print_list()
    elif args.random:
        shoplist.choose_random(count=args.random, write=args.save)
        shoplist.print_list(write=args.save)
    else:
        menu_items = args.recipes
        if not menu_items:
            sys.exit('You must supply at least one recipe'
                     ' to build your shopping list from!')

        for item in menu_items:
            shoplist.update(item)
        #shoplist.update_remote()
        shoplist.print_list(write=args.save)

def cmd_dump(args):
    """Dump recipe data in 1 of three formats."""
    recipe = Recipe(args.source)
    recipe.dump_to_screen(args.data_type)

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

    recipe = Recipe(args.source)
    xml = recipe.get_xml_data()
    file_name = utils.get_file_name_from_recipe(args.source, 'xml')
    file_name = os.path.join(output_dir, file_name)

    if args.xml:
        file_name = utils.get_file_name_from_recipe(args.source, 'xml')
        print(utils.msg("Writing to file: {}".format(file_name), "INFORM"))
        with open(file_name, "w") as file:
            file.write(str(xml))

    if args.recipe:
        file_name = utils.get_file_name_from_recipe(args.source)
        src = recipe.source
        dst = os.path.join(output_dir, file_name)
        if os.path.isfile(dst):
            sys.exit(utils.msg("File already exists.", "ERROR"))
        else:
            shutil.copyfile(src, dst)

def cmd_ocr(args):
    """Optical character recognition"""
    recipe = RecipeOCR(args.source)
    if args.imprt:
        recipe.save()
    else:
        print(recipe)

def cmd_show(args):
    """Show the statistics information of the recipe database."""
    utils.stats(args.verbose)

def version():
    """Print pyrecipe version information."""
    version_info()

# mainly for the testsuite
__all__ = [c for c in dir() if c.startswith('cmd_')] + ['get_parser']

## End command funtions

def build_recipe_database():
    """Build the recipe database."""
    database = DBConn()
    database.create_database()
    for item in config.RECIPE_DATA_FILES:
        recipe = Recipe(item)
        database.add_recipe(recipe)

def subparser_print(subparser):
    """Subparser for print command."""
    parser_print = subparser.add_parser(
        "print",
        help="Print the recipe to screen"
    )
    parser_print.add_argument(
        "source",
        help="Recipe, file path, or url"
    )
    parser_print.add_argument(
        "--yield",
        default=0,
        nargs='?',
        metavar='N',
        type=int,
        dest="recipe_yield",
        help="Specify a yield for the recipe."
    )

def subparser_edit(subparser):
    """Subparser for edit command."""
    parser_edit = subparser.add_parser(
        "edit",
        help="Edit a recipe data file"
    )
    parser_edit.add_argument(
        "source",
        type=str,
        help="Recipe to edit"
    )

def subparser_add(subparser):
    """Subparser for add command."""
    parser_add = subparser.add_parser("add", help='Add a recipe')
    parser_add.add_argument("name", help='Name of the recipe to add')

def subparser_remove(subparser):
    """Subparser for remove command."""
    parser_remove = subparser.add_parser("remove", help='Delete a recipe')
    parser_remove.add_argument(
        "source",
        help='Recipe to delete'
    )

def subparser_make(subparser):
    """Subparser for make command."""
    parser_make = subparser.add_parser(
        "make",
        help='Make a recipe using the urwid automated script'
    )
    parser_make.add_argument(
        "source",
        help='Recipe to make'
    )

def subparser_search(subparser):
    """Subparser for search command."""
    parser_search = subparser.add_parser(
        "search",
        help="Search the recipe database"
    )
    parser_search.add_argument(
        "search",
        nargs="*",
        help="Search the recipe database"
    )

def subparser_shop(subparser):
    """Subparser for shop command."""
    parser_shop = subparser.add_parser("shop", help='Make a shopping list')
    parser_shop.add_argument(
        "recipes",
        nargs="*",
        help='List of recipe to compile shopping list'
    )
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
        "-n",
        "--new",
        action="store_true",
        help="Make a new list. The old list will be overwritten."
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
        help="Pick n random recipes for the week"
    )
    parser_shop.add_argument(
        "-s",
        "--save",
        action="store_true",
        help="Save the current shopping list."
    )

def subparser_dump(subparser):
    """Subparser for dump command."""
    parser_dump = subparser.add_parser(
        "dump",
        help="Dump yaml or xml representation of recipe to stdout"
    )
    parser_dump.add_argument(
        "source",
        help="Recipe to dump data from"
    )
    parser_dump.add_argument(
        "-x",
        "--xml",
        dest="data_type",
        action="store_const",
        const="xml",
        help="Dump source xml tree to standard output"
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

def subparser_export(subparser):
    """Subparser for export command."""
    parser_export = subparser.add_parser(
        "export",
        help="Export recipes in xml format"
    )
    parser_export.add_argument(
        "source",
        help="Sorce file to export"
    )
    parser_export.add_argument(
        "-o",
        "--output-dir",
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
        action='store_true',
        help="Export file in xml format"
    )
    parser_export.add_argument(
        "-r",
        "--recipe",
        action='store_true',
        help="Export recipe file"
    )

def subparser_ocr(subparser):
    """Subparser for ocr command."""
    parser_ocr = subparser.add_parser(
        "ocr",
        help="Pyrecipe Optical Character Recognition"
    )
    parser_ocr.add_argument(
        "source",
        help="File to read"
    )
    parser_ocr.add_argument(
        "-i",
        "--import",
        dest="imprt",
        action="store_true",
        help="Import the data into the database"
    )

def subparser_show(subparser):
    """Subparser for show command."""
    parser_show = subparser.add_parser(
        "show",
        help="Show statistic from the recipe database"
    )
    parser_show.add_argument(
        "-v",
        "--verbose",
        help="Show more statistics about the recipe database"
    )

def get_parser():
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
        action="store_true",
        help="Print version and exit"
    )

    # Subparsers start here
    subparser = parser.add_subparsers(dest='subparser')
    subparser_print(subparser)
    subparser_edit(subparser)
    subparser_add(subparser)
    subparser_remove(subparser)
    subparser_make(subparser)
    subparser_search(subparser)
    subparser_shop(subparser)
    subparser_dump(subparser)
    subparser_export(subparser)
    subparser_ocr(subparser)
    subparser_show(subparser)

    return parser

def main():
    """Main entry point of recipe_tool."""
    # Build the databse first if it does not exist.
    # A good way to rebuild the db is to delete the
    # db file.
    db_exists = os.path.exists(config.DB_FILE)
    recipe_exists = len(config.RECIPE_DATA_FILES) > 0
    if not db_exists and recipe_exists:
        print('Building recipe database...')
        build_recipe_database()

    parser = get_parser()
    args = parser.parse_args()
    if len(sys.argv) == 1:
        sys.exit(parser.print_help())
    elif len(sys.argv) == 2 and args.verbose:
        # if recipe_tool is invoked with only a
        # verbose flag it causes an exception so
        # here we offer help if no other flags are given
        sys.exit(parser.print_help())
    
    
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
        'ocr': cmd_ocr,
        'show': cmd_show,
    }
    if args.version:
        version()
    else:
        case[args.subparser](args)
