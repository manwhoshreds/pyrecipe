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

from pyrecipe import VER_STR
from pyrecipe.views import View
from pyrecipe.controllers import Controller



def view_recipe(args):
    """Read and print a recipe"""
    rec = PyRecipe().read_recipe(args.source)
    View.view_recipe(rec, args.verbose)

def add_recipe(args):
    """Create a recipe"""
    pyrec = PyRecipe()
    rec = pyrec.read_recipe(args.source)
    new_rec = View.create_recipe(rec)
    pyrec.create_recipe(new_rec)

def edit_recipe(args):
    """Update a recipe"""
    pyrec = PyRecipe()
    rec = pyrec.read_recipe(args.source)
    new_rec = View.edit_recipe(rec)
    pyrec.update_recipe(new_rec)

def remove_recipe(args):
    """Delete a recipe"""
    try:
        rec = PyRecipe().read_recipe(args.source)
        answer = input(f"Are you sure your want to delete {args.source}? yes/no ")
        pyrec = PyRecipe()
        if answer.strip() in ('yes', 'y'):
            pyrec.delete_recipe(args.source.lower())
            sys.exit(View.display_message('recipe_deleted', 'INFORM', args.source))

        sys.exit(View.display_message('recipe_not_deleted', 'INFORM', args.source))
    except RecipeNotFound:
        sys.exit(View.display_message('recipe_not_found', 'ERROR', args.source))

def subparser_add(subparser):
    """Subparser for add command."""
    parser_add = subparser.add_parser("add", help='Add a recipe')
    parser_add.add_argument("source", help='Name of the recipe to add')

def subparser_view(subparser):
    """Subparser for view command."""
    parser = subparser.add_parser(
        "view",
        help="Print the recipe to standard output"
    )
    parser.add_argument(
        "source",
        help="Recipe, file path, or url"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Increase the verbosity of output. \
              Only works with the view command."
    )
    parser.add_argument(
        "--recipe-yield",
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
        help="Recipe to delete"
    )

def get_parser():
    """Parse args for recipe_tool."""
    parser = argparse.ArgumentParser(
        description="Recipe_tool has tab completion functionality. \
                     After adding a recipe, simply run recipe_tool \
                     view <TAB><TAB> to view whats available.",
        add_help=False
    )
    parser.add_argument(
        "-h", "--help",
        action='help',
        help="Show this help message and quit"
    )
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help="Print version and exit"
    )

    subparser = parser.add_subparsers(dest='subparser')
    subparser_add(subparser)
    subparser_view(subparser)
    subparser_edit(subparser)
    subparser_remove(subparser)
    return parser


def main():
    """Main entry point of pyrecipe."""

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
        'add': add_recipe,
        'view': view_recipe,
        'edit': edit_recipe,
        'remove': remove_recipe,
    }

    if args.version:
        sys.exit(VER_STR)
    else:
        case[args.subparser](args)

if __name__ == '__main__':
    main()
