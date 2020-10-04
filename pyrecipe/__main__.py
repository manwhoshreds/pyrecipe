#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
    recipe_tool
    ~~~~~~~~~~~

    recipe_tool is the frontend commandline interface to
    the pyrecipe library.
"""
import sys
import argparse

import pyrecipe.utils as utils
from pyrecipe import VER_STR
from pyrecipe.backend import Chef
from pyrecipe.user_interface import View


class RecipeController:
    """Controller for the pyrecipe program"""


    def __init__(self, Chef, View):
        self.chef = Chef()
        self.view = View()


    def create_recipe(self, args):
        """Create a recipe"""
        empty = self.chef.init_recipe(args.source)
        recipe = self.view.create_recipe(empty)
        self.chef.create_recipe(recipe)


    def read_recipe(self, args):
        """Read and print a recipe"""
        recipe = self.chef.read_recipe(args.source)
        self.view.print_recipe(recipe, args.verbose)


    def update_recipe(self, args):
        """Update a recipe"""
        recipe = self.chef.read_recipe(args.source)
        new_recipe = self.view.edit_recipe(recipe)
        self.chef.update_recipe(new_recipe)


    def delete_recipe(self, args):
        """Delete a recipe"""
        answer = input("Are you sure your want to delete {}? yes/no "
                       .format(args.source))
        if answer.strip() == 'yes':
            self.Chef.delete_recipe(args.source)
            msg = '{} has been deleted'.format(args.source)
            sys.exit(utils.msg(msg, 'INFORM'))

        msg = '{} was not deleted'.format(args.source)
        sys.exit(utils.msg(msg, 'INFORM'))


def subparser_add(subparser):
    """Subparser for add command."""
    parser_add = subparser.add_parser("add", help='Add a recipe')
    parser_add.add_argument("source", help='Name of the recipe to add')


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


def subparser_remove(subparser):
    """Subparser for remove command."""
    parser_remove = subparser.add_parser("remove", help='Delete a recipe')
    parser_remove.add_argument(
        "source",
        help='Recipe to delete'
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
    subparser_add(subparser)
    subparser_print(subparser)
    subparser_edit(subparser)
    subparser_remove(subparser)
    return parser


def main():
    """Main entry point of recipe_tool."""

    parser = get_parser()
    args = parser.parse_args()
    if len(sys.argv) == 1:
        sys.exit(parser.print_help())
    elif len(sys.argv) == 2 and args.verbose:
        # if recipe_tool is invoked with only a
        # verbose flag it causes an exception so
        # here we offer help if no other flags are given
        sys.exit(parser.print_help())

    rc = RecipeController(Chef, View)
    case = {
        'add': rc.create_recipe,
        'print': rc.read_recipe,
        'edit': rc.update_recipe,
        'remove': rc.delete_recipe,
    }
    if args.version:
        sys.exit(VER_STR)
    else:
        case[args.subparser](args)

if __name__ == '__main__':
    main()
