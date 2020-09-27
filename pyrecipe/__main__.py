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
from pyrecipe.user_interface import View


# For the testsuite
__all__ = [c for c in dir() if c.startswith('cmd_')] + ['get_parser']


class RecipeController:

    
    def __init__(self, RecipeDB, View):
        self.RecipeDB = RecipeDB
        self.View = View

    
    def print_recipe(self, args):
        try: 
            recipe = RecipeDB().read_recipe(args.source)
            self.View.print_recipe(recipe, args.verbose)
        except RecipeNotFound as e:
            exit(e)


    def create_recipe(self, args):
        recipe = self.view(args.name, add=True).start()
        self.RecipeDB().add_recipe(recipe)
    
    
    def delete_recipe(self, args):
        answer = input("Are you sure your want to delete {}? yes/no "
                       .format(args.source))
        if answer.strip() == 'yes':
            self.RecipeDB().delete_recipe(args.source)
            msg = '{} has been deleted'.format(args.source)
            sys.exit(utils.msg(msg, 'INFORM'))

        msg = '{} was not deleted'.format(args.source)
        sys.exit(utils.msg(msg, 'INFORM'))
    

    def edit_recipe(self, args):
        recipe = RecipeDB().read_recipe(args.source)
        edit_recipe = self.view(recipe).start()
        edit_recipe.print_recipe()


def cmd_print(args):
    """Print a recipe to stdout."""
    RecipeController(RecipeDB, View).print_recipe(args)


def cmd_add(args):
    """Add a recipe to the recipe store."""
    RecipeController(RecipeDB, View).create_recipe(args)


def cmd_edit(args):
    """Edit a recipe using the urwid console interface."""
    RecipeController(RecipeDB, View).edit_recipe(args)


def cmd_remove(args):
    """Delete a recipe from the recipe store."""
    RecipeController(RecipeDB, View).delete_recipe(args)

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
    recipe_data_dir = os.path.expanduser("~/.config/pyrecipe/recipe_data")
    for item in os.listdir(recipe_data_dir):
        r = Recipe(os.path.join(recipe_data_dir, item))
        database.add_recipe(r)


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
        'show': cmd_show,
    }
    if args.version:
        version()
    else:
        case[args.subparser](args)

if __name__ == '__main__':
    main()
