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
from pyrecipe.view import View
from pyrecipe.backend import PyRecipe, RecipeNotFound  # , RecipeAlreadyStored

def create_recipe(args, pyrec):
    rec = pyrec.get_recipe(args.source)
    new_rec = View.create_recipe(rec)
    pyrec.create_recipe(new_rec)

def view_recipe(args, pyrec):
    rec = pyrec.get_recipe(args.source)
    View.print_recipe(rec, args.verbose)

def update_recipe(args, pyrec):
    rec = pyrec.get_recipe(args.source)
    new_rec = View.edit_recipe(rec)
    pyrec.update_recipe(new_rec)

def delete_recipe(args, pyrec):
    """
    Deletes a recipe from the database after user confirmation.

    Args:
        args: The parsed command-line arguments containing the source recipe.
        pyrec: The PyRecipe object used to interact with the recipe database.

    Raises:
        RecipeNotFound: If the recipe cannot be found in the database.
    """
    try:
        rec = pyrec.get_recipe(args.source)
        answer = input(f"Are you sure you want to delete {args.source}? yes/no ")
        if answer.strip().lower() in ('yes', 'y'):
            pyrec.delete_recipe(args.source.lower())
            sys.exit(View.display_message('recipe_deleted', 'INFORM', args.source))

        sys.exit(View.display_message('recipe_not_deleted', 'INFORM', args.source))
    except RecipeNotFound:
        sys.exit(View.display_message('recipe_not_found', 'ERROR', args.source))
    except Exception as e:
        sys.exit(View.display_message('unexpected_error', 'ERROR', str(e)))

def subparser_add(subparser):
    parser_add = subparser.add_parser("add", help='Add a recipe')
    parser_add.add_argument("source", help='Name of the recipe to add')

def subparser_view(subparser):
    parser = subparser.add_parser(
        "view",
        help="Display the recipe on screen"
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
    parser_remove = subparser.add_parser("remove", help='Delete a recipe')
    parser_remove.add_argument(
        "source",
        help="Recipe to delete"
    )

def get_parser():
     
    parser = argparse.ArgumentParser(
        description="Recipe_tool has tab completion functionality.\n"
                    "After adding a recipe, run: recipe_tool view <TAB><TAB>\n"
                    "to view available recipes.",
        add_help=False
    )
    parser.add_argument(
            "-h", 
            "--help", 
            action='help', 
            help="Show this help message and quit"
    )
    parser.add_argument(
            "-v", 
            "--verbose", 
            action="store_true", 
            help="Increase output verbosity. Works with 'view'."
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
    """
    Main entry point for recipe_tool. Processes command-line arguments 
    and runs the relevant functions. If no subcommand is provided, or an 
    invalid subcommand is given, it displays the help message.
    """
    parser = get_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        sys.exit(parser.print_help())
    elif len(sys.argv) == 2 and args.verbose:
        sys.exit(parser.print_help())

    if args.version:
        sys.exit(VER_STR)

    pyrec = PyRecipe()
    case = {
        'add': lambda a: create_recipe(a, pyrec),
        'view': lambda a: view_recipe(a, pyrec),
        'edit': lambda a: update_recipe(a, pyrec),
        'remove': lambda a: delete_recipe(a, pyrec),
    }

    if args.subparser:
        case[args.subparser](args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

