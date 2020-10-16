# -*- encoding: UTF-8 -*-
"""
    pyrecipe.backend.chef
    ~~~~~~~~~~~~~~~~~~~~~
    The recipe module contains the main recipe
    class used to interact with ORF (open recipe format) files.
    You can simply print the recipe or print the xml dump.

    - Recipe: The main recipe class is responsible for caching all the
              data associated with an Open Recipe Format file. Give the
              recipe instance an ORF source and all data can be accessed
              like a python dict. You can also assign new attributes or
              change current ones. Use the print_recipe() method to print
              the recipe to standard output and save() to save the data
              back to the same file or one of your own choosing.

              An instance of a recipe class contains all the information
              in a recipe.

              The current recipe data understood by the recipe class can
              be found in the class variable: ORF_KEYS

    - Ingredient: takes a string or a dict of ingredient data

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""
import os
import re
import sys
from zipfile import ZipFile, BadZipFile

from ruamel.yaml import YAML

from pyrecipe.backend.webscraper import scraper, MalformedUrlError, SiteNotScrapeable
from pyrecipe.backend.database import RecipeDB, DB_FILE
from pyrecipe.backend.recipe import Recipe
import pyrecipe.utils as utils


HTTP_RE = re.compile(r'^https?\://')
yaml = YAML(typ='safe')
yaml.default_flow_style = False


class Chef:
    """Factory class for the pyrecipe model layer
    
    The chef class can recieve one of three inputs:
    a recipe name, url or filename.
    """

    
    def __init__(self):
        self.db = RecipeDB()
    
    def _check_source(self, source):
        if os.path.isfile(source):
            try:
                with ZipFile(source, 'r') as zfile:
                    try:
                        with zfile.open('recipe.yaml', 'r') as stream:
                            recipe = Recipe(yaml.load(stream))
                            return recipe
                    except KeyError:
                        sys.exit(utils.msg("Can not find recipe.yaml. Is this "
                                           "really a recipe file?", "ERROR"))
            except BadZipFile as e:
                sys.exit(utils.msg("{}".format(e), "ERROR"))
        else:
            recipe = source
        try:
            return scraper.scrape(source)
        except MalformedUrlError:
            pass
        except SiteNotScrapeable as e:
            return e

        return recipe

    
    def __repr__(self):
        return '<Chef({})>'.format(self.source)
    

    def create_recipe(self, recipe):
        recipe = self._check_source(recipe)
        test = self.db.create_recipe(recipe)
        return test


    def read_recipe(self, recipe):
        recipe = self._check_source(recipe)
        test = self.db.read_recipe(recipe)
        return test

    def update_recipe(self, recipe):
        self.db.update_recipe(recipe)

    def delete_recipe(self, recipe):
        pass

    def init_recipe(self, recipe):
        """Return an empty recipe"""
        return Recipe(recipe)



if __name__ == '__main__':
    import shutil
    env = shutil.which('python')
    if '.virtual' in env:
        print('hello')
        def build_recipe_database():
            """Build the recipe database."""
            database = RecipeDB()
            database.create_database()
            recipe_data_dir = os.path.expanduser("~/.config/pyrecipe/recipe_data")
            chef = Chef()
            for item in os.listdir(recipe_data_dir):
                r = chef.create_recipe(os.path.join(recipe_data_dir, item))
                print('Adding...    {}'.format(item))

        # Build the databse first if it does not exist.
        db_exists = os.path.isfile(DB_FILE)
        if db_exists:
            os.remove(DB_FILE)
        recipe_data_dir = os.path.expanduser("~/.config/pyrecipe/recipe_data")
        recipe_exists = len(os.listdir(recipe_data_dir)) > 0
        if recipe_exists:
            print('Building recipe database...')
            build_recipe_database()
    else:
        sys.exit(print('You are not working in a development environment'))
    
