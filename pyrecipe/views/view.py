# -*- coding: utf-8 -*-
"""
    pyrecipe.user_interface.view
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The pyrecipe presentation layer

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""

from termcolor import colored

from .editor import RecipeEditor
from pyrecipe import utils


def divider(m):
    """Prints a divider"""
    return colored('~' * m, 'white')


class View:
    """View class for the pyrecipe program"""

    @staticmethod
    def view_recipe(recipe, verbose=False):
        """Print the recipe to standard output."""

        recipe_str = colored(recipe.name.title(), 'cyan', attrs=['bold'])
        recipe_str += f"\n\nDish Type: {recipe.dish_type}"
        recipe_str += f"\nPrep Time: {recipe.prep_time}"
        recipe_str += f"\nCook Time: {recipe.cook_time}"
        recipe_str += f"\nAuthor: {recipe.author}"

        extra_info = False
        if verbose:
            if recipe.source_url:
                recipe_str += f"\nURL: {recipe.source_url}"
                extra_info = True
            if recipe.notes:
                recipe_str += colored("\n\nNotes:", "cyan")
                wrapped = utils.wrap(recipe.notes)
                for index, note in wrapped:
                    recipe_str += colored(f"\n{index}", "yellow")
                    recipe_str += note
                extra_info = True

            if not extra_info:
                recipe_str += '\n'
                recipe_str += utils.message('No additional information', 'WARN')

        recipe_str += f"\n\n{divider(79)}"
        recipe_str += colored("\nIngredients:", "cyan", attrs=['underline'])

        # Ingredients
        ingreds = recipe.get_ingredients()
        for item, ingreds in ingreds.items():
            if item:
                recipe_str += colored(f"\n\n{item.title()}", "cyan")
            for ingred in ingreds:
                recipe_str += f"\n{ingred}"

        recipe_str += f"\n\n{divider(79)}"

        # Method
        recipe_str += colored("\nMethod:", "cyan", attrs=["underline"])
        wrapped = utils.wrap(recipe.steps)
        for index, step in wrapped:
            recipe_str += f"\n{colored(index, 'yellow')}"
            recipe_str += step

        print(recipe_str)

    @staticmethod
    def create_recipe(recipe):
        """Create recipe"""
        return RecipeEditor(recipe).start()

    @staticmethod
    def edit_recipe(recipe):
        """Edit recipe"""

        return RecipeEditor(recipe).start()

    @staticmethod
    def display_message(message, level, recipe=None):
        """Display Message"""
        print(utils.message(message, level, recipe))
