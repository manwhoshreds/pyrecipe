# -*- coding: utf-8 -*-
"""
    pyrecipe.user_interface.view
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The pyrecipe presentation layer
    
    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""

import pyrecipe.utils as utils
from termcolor import colored
from pyrecipe.recipe.recipe_numbers import RecipeNum


def print_recipe(recipe, verbose=False, color=True):
    """Print the recipe to standard output."""
    print(verbose)
    recipe_str = colored(recipe.name.title(), 'cyan', attrs=['bold'])
    recipe_str += "\n\nDish Type: {}".format(str(recipe.dish_type))
    for item in ('prep_time', 'cook_time', 'bake_time'):
        if recipe[item]:
            recipe_str += "\n{}: {}".format(
                item.replace('_', ' ').title(),
                utils.mins_to_hours(RecipeNum(recipe[item]))
            )

    if recipe.oven_temp:
        recipe_str += "\nOven temp: {}".format(recipe.oven_temp)

    if recipe.author:
        recipe_str += "\nAuthor: {}".format(recipe.author)

    extra_info = False
    if verbose:
        if recipe.price:
            recipe_str += "\nPrice: {}".format(recipe.price)
            extra_info = True
        if recipe.source_url:
            recipe_str += "\nURL: {}".format(recipe.source_url)
            extra_info = True
        if recipe.categories:
            recipe_str += ("\nCategory(s): {}"
                           .format(", ".join(recipe.categoies)))
            extra_info = True
        if recipe.notes:
            recipe_str += colored("\n\nNotes:", "cyan")
            wrapped = utils.wrap(recipe.notes)
            for index, note in wrapped:
                recipe_str += colored("\n{}".format(index), "yellow")
                recipe_str += note
            extra_info = True

        if not extra_info:
            recipe_str += '\n'
            recipe_str += utils.msg('No additional information', 'WARN')

    recipe_str += "\n\n{}".format(utils.S_DIV(79))
    recipe_str += colored("\nIngredients:", "cyan", attrs=['underline'])

    # Put together all the ingredients
    ingreds, named_ingreds = recipe.get_ingredients()
    for ingred in ingreds:
        recipe_str += "\n{}".format(ingred)

    if named_ingreds:
        for item in named_ingreds:
            recipe_str += colored("\n\n{}".format(item.title()), "cyan")

            for ingred in named_ingreds[item]:
                recipe_str += "\n{}".format(ingred)

    recipe_str += "\n\n{}".format(utils.S_DIV(79))
    recipe_str += colored("\nMethod:", "cyan", attrs=["underline"])

    # print steps
    wrapped = utils.wrap(recipe.method)
    for index, step in wrapped:
        recipe_str += "\n{}".format(colored(index, "yellow"))
        recipe_str += step

    print(recipe_str)

class View:

    @staticmethod
    def print_recipe(recipe, *args, **kwargs):
        print_recipe(recipe)
