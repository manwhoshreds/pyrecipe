import os
import shutil

from pyrecipe.backend.database import RecipeDB, DB_FILE
from .recipe import Recipe
ENV = shutil.which('python')

if '.virtual' in ENV:
    def build_recipe_database():
        """Build the recipe database."""
        database = RecipeDB()
        database.create_database()
        recipe_data_dir = os.path.expanduser("~/.config/pyrecipe/recipe_data")
        for item in os.listdir(recipe_data_dir):
            rec = Recipe(os.path.join(recipe_data_dir, item))
            rec.create_recipe()
            print('Adding: {}'.format(rec.name))

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
    sys.exit(
        print('Cannot build database. You are not working in a ',
              'development environment')
    )

