# -*- coding: utf-8 -*-
"""
    pyrecipe.user_interface.view
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The pyrecipe presentation layer

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""

from termcolor import colored

import pyrecipe.utils as utils
from pyrecipe.backend.recipe_numbers import RecipeNum
from pyrecipe.editor import RecipeEditor
from pyrecipe.helpers import wrap


S_DIV = lambda m: colored('~' * m, 'white')


class View:
    """View class for the pyrecipe program"""

    @staticmethod
    def print_recipe(recipe, verbose=False):
        """Print the recipe to standard output."""
        
        recipe_str = colored(recipe.name.title(), 'cyan', attrs=['bold'])
        recipe_str += "\n\nDish Type: {}".format(str(recipe.dish_type))
        recipe_str += "\nPrep Time: {}".format(RecipeNum(recipe.prep_time))
        recipe_str += "\nCook Time: {}".format(RecipeNum(recipe.cook_time))
        recipe_str += "\nAuthor: {}".format(recipe.author)

        extra_info = False
        if verbose:
            if recipe.source_url:
                recipe_str += "\nURL: {}".format(recipe.source_url)
                extra_info = True
            if recipe.notes:
                recipe_str += colored("\n\nNotes:", "cyan")
                wrapped = wrap(recipe.notes)
                for index, note in wrapped:
                    recipe_str += colored("\n{}".format(index), "yellow")
                    recipe_str += note
                extra_info = True

            if not extra_info:
                recipe_str += '\n'
                recipe_str += utils.msg('No additional information', 'WARN')

        recipe_str += "\n\n{}".format(S_DIV(79))
        recipe_str += colored("\nIngredients:", "cyan", attrs=['underline'])

        # Ingredients
        ingreds = recipe.get_ingredients()
        for item, ingreds in ingreds.items():
            if item:
                recipe_str += colored("\n\n{}".format(item.title()), "cyan")
            for ingred in ingreds:
                recipe_str += "\n{}".format(ingred)

        recipe_str += "\n\n{}".format(S_DIV(79))

        # Method
        recipe_str += colored("\nMethod:", "cyan", attrs=["underline"])
        wrapped = wrap(recipe.steps)
        for index, step in wrapped:
            recipe_str += "\n{}".format(colored(index, "yellow"))
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
