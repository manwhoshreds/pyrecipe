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
import argparse

import pyrecipe.utils as utils
from pyrecipe.recipe import Recipe
from pyrecipe.db import RecipeDB, DB_FILE, RecipeNotFound
from pyrecipe.webscraper import SCRAPEABLE_SITES
from pyrecipe import __scriptname__, version_info
from pyrecipe.console_gui import RecipeEditor


# For the testsuite
__all__ = [c for c in dir() if c.startswith('cmd_')] + ['get_parser']


class RecipeController:

    def __init__(self, RecipeDB, view):
        self.RecipeDB = RecipeDB
        self.view = view

    def print_recipe(self, args):
        try: 
            recipe = RecipeDB().read_recipe(args.source)
            recipe.print_recipe(args.verbose)
        except RecipeNotFound as e:
            exit(e)


    def create_recipe(self):
        pass

    def edit_recipe(self, args):
        recipe = RecipeDB().read_recipe(args.source)
        edit_recipe = self.view(recipe).start()
        edit_recipe.print_recipe()


def cmd_print(args):
    """Print a recipe to stdout."""
    RecipeController(RecipeDB, 'print').print_recipe(args)


def cmd_add(args):
    """Add a recipe to the recipe store."""
    name = args.name.strip()
    RecipeEditor(name, add=True).start()


def cmd_edit(args):
    """Edit a recipe using the urwid console interface."""
    RecipeController(RecipeDB, RecipeEditor).edit_recipe(args)


def cmd_remove(args):
    """Delete a recipe from the recipe store."""
    recipe = Recipe(args.source)
    answer = input("Are you sure your want to delete {}? yes/no "
                   .format(recipe.name))
    if answer.strip() == 'yes':
        os.remove(recipe.file_name)
        print("{} has been deleted".format(recipe.name))
        return recipe.uuid

    print("{} not deleted".format(recipe.name))
    return None

def cmd_search(args):
    """Search the recipe database."""
    search = args.search
    #for item in resp['recipes']:
    #    print(item['name'].title())
    #sys.exit(0)

    results = sorted(DBInfo().search(search))
    numres = len(results)
    if numres == 0:
        sys.exit(utils.msg(
            "Your search for \"{}\" produced no results".format(args.search),
            "INFORM"))
    results = "\n".join(s.lower() for s in results)
    sys.exit(results)


def cmd_dump(args):
    """Dump recipe data in 1 of three formats."""
    recipe = Recipe(args.source)
    sys.exit(recipe.dump_data(args.data_type))


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
        if args.all:
            output_dir = os.path.realpath('recipes')
            os.makedirs(output_dir)
        else:
            output_dir = os.getcwd()

    if args.all:
        for item in config.RECIPE_DATA_FILES:
            recipe = Recipe(item)
            recipe.export(args.data_type, output_dir)
        sys.exit(0)

    recipe = Recipe(args.source)
    recipe.export(args.data_type, output_dir)


def cmd_show(args):
    """Show the statistics information of the recipe database."""
    dbinfo = DBInfo()
    if args.sites:
        print('\n'.join(SCRAPEABLE_SITES))
    elif args.dish_type:
        print('\n'.join(dbinfo.get_recipes_by_dishtype(args.dish_type)))
    else:
        sys.exit(utils.stats(args.verbose))


def version():
    """Print pyrecipe version information."""
    version_info()


def build_recipe_database():
    """Build the recipe database."""
    database = RecipeDB()
    database.create_database()
    for item in config.RECIPE_DATA_FILES:
        recipe = Recipe(item)
        database.add_recipe(recipe)


def subparser_print(subparser):
    """Subparser for print command."""
    parser = subparser.add_parser(
        "print",
        help="Print the recipe to screen"
    )
    parser.add_argument(
        "source",
        help="Recipe, file path, or url"
    )
    parser.add_argument(
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
    parser = subparser.add_parser(
        "edit",
        help="Edit a recipe data file"
    )
    parser.add_argument(
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
        "-j",
        "--json",
        dest="data_type",
        action="store_const",
        const="json",
        help="Dump source json"
    )


def subparser_export(subparser):
    """Subparser for export command."""
    parser_export = subparser.add_parser(
        "export",
        help="Export recipes in xml format"
    )
    parser_export.add_argument(
        "source",
        nargs="?",
        help="Sorce file to export"
    )
    parser_export.add_argument(
        "-o",
        "--output-dir",
        metavar="dir",
        type=str,
        nargs="?",
        help="Choose a directory to output file"
    )
    parser_export.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Export all files in the database"
    )
    parser_export.add_argument(
        "-x",
        "--xml",
        dest="data_type",
        action='store_const',
        const='xml',
        help="Export file in xml format"
    )
    parser_export.add_argument(
        "-r",
        "--recipe",
        dest="data_type",
        action='store_const',
        const='recipe',
        help="Export recipe file"
    )


def subparser_show(subparser):
    """Subparser for show command."""
    parser_show = subparser.add_parser(
        "show",
        help="Show statistic from the recipe database"
    )
    parser_show.add_argument(
        "-d",
        "--dish-type",
        metavar="DISHTYPE",
        help="List sites that can be scraped"
    )
    parser_show.add_argument(
        "--scrapeable-sites",
        action="store_true",
        dest="sites",
        help="List sites that can be scraped"
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

    subparser = parser.add_subparsers(dest='subparser')
    subparser_print(subparser)
    subparser_edit(subparser)
    subparser_add(subparser)
    subparser_remove(subparser)
    subparser_search(subparser)
    subparser_dump(subparser)
    subparser_export(subparser)
    subparser_show(subparser)

    return parser


def main():
    """Main entry point of recipe_tool."""
    # Build the databse first if it does not exist.
    # A good way to rebuild the db is to delete the
    # db file.
    db_exists = os.path.exists(DB_FILE)
    recipe_data_dir = os.path.expanduser("~/.config/pyrecipe/recipe_data")
    recipe_exists = len(os.listdir(recipe_data_dir)) > 0
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
        'search': cmd_search,
        'dump': cmd_dump,
        'export': cmd_export,
        'show': cmd_show,
    }
    if args.version:
        version()
    else:
        case[args.subparser](args)

if __name__ == '__main__':
    import os
    print(os.path.listdir())
    #main()
