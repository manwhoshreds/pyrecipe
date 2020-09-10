"""
    pyreicpe.db
    ~~~~~~~~~~~

    The main database connection file for pyrecipe. This module handles
    the connection, query, and building of the database.
"""
import os
import sqlite3

from pyrecipe.config import DB_FILE



def read_sql():
    with open("tables.sql") as fi:
        commands = fi.read().split(';')

    return commands
        

class RecipeDB:
    """A database class for pyrecipe."""
    def __init__(self):
        try:
            self.conn = sqlite3.connect(DB_FILE)
        except sqlite3.OperationalError:
            sys.exit('Something unexpected happened....')
        self.c = self.conn.cursor()
        self.c.execute("PRAGMA foreign_keys = ON")

    def add(self, recipe):
        '''Add a recipe to the database.'''
        recipe_data = [(
            recipe.uuid,
            recipe.name,
            recipe.dish_type,
            recipe.author,
            recipe.tags,
            recipe.categories,
            recipe.price,
            recipe.source_url
        )]
        self.c.executemany(
            '''INSERT OR REPLACE INTO recipes (
                recipe_uuid,
                name,
                dish_type,
                author,
                tags,
                categories,
                price,
                source_url
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?)''', recipe_data
        )
        recipe_data_search = [(
            recipe.name,
            recipe.author,
            recipe.tags,
            recipe.categories,
        )]
        #self.c.executemany(
        #    '''INSERT OR REPLACE INTO recipesearch (
        #        name,
        #        author,
        #        tags,
        #        categories
        #        ) VALUES(?, ?, ?, ?)''', recipe_data_search
        #)
        for ingredient in recipe.ingredients:
            ingredient_data_search = [(
                recipe.name,
                ingredient.name
            )]
            #self.c.executemany(
            #    '''INSERT OR REPLACE INTO ingredientsearch (
            #        name,
            #        ingredient
            #        ) VALUES(?, ?)''', ingredient_data_search
            #)
        self._commit()
        recipe_id = self.query(
            "SELECT recipe_id FROM recipes WHERE name = \'{}\'"
            .format(recipe.name)
        )
        print(recipe.get_ingredients())
        for item in recipe.get_ingredients()[0]:
            self.c.execute('''INSERT OR REPLACE INTO Ingredients (
                                recipe_id,
                                ingredient_str
                                ) VALUES(?, ?)''', (recipe_id[0][0], item))
    
        if recipe.get_ingredients(fmt='string')[1]:
            for item, ingreds in recipe.get_ingredients(fmt='string')[1].items():
                for ingred in ingreds:
                    self.c.execute('''INSERT OR REPLACE INTO named_ingredients (
                                        recipe_id,
                                        alt_name,
                                        ingredient_str
                                        ) VALUES(?, ?, ?)''', (recipe_id[0][0], item, ingred))
        
        self._commit()

    def get_recipe(self, recipe):
        test = self.query("SELECT * FROM recipes WHERE name=\'{}\'".format(recipe))
        return test

    def __del__(self):
        self.conn.close()

    def _commit(self):
        self.conn.commit()

    def execute(self, command):
        self.c.execute(command)
        self._commit()

    def query(self, command):
        if not command.lower().startswith('select'):
            raise TypeError('query string must be one of select')
        try:
            query = self.c.execute(command)
            result = query.fetchall()
        except sqlite3.OperationalError:
            result = []
        return result

    def create_database(self):
        """Create the recipe database."""
        with open("tables.sql") as fi:
            commands = fi.read().split(';')

        for command in commands:
            self.c.execute(command)

def update_db(save_func):
    """Decorater for updating pyrecipe db."""
    def wrapper(recipe):
        db = RecipeDB()
        db.add_recipe(recipe)
        save_func(recipe)
    return wrapper

def delete_recipe(delete_func):
    """Decorater for updating pyrecipe db."""
    def wrapper(args):
        deleted_file = delete_func(args)
        if deleted_file:
            db = RecipeDB()
            sql = (
                "DELETE FROM recipes WHERE recipe_uuid = \'{}\'"
                .format(deleted_file)
            )
            db.execute(sql)
    return wrapper

if __name__ == '__main__':
    from pyrecipe.recipe import Recipe
    r = Recipe('/home/michael/.config/pyrecipe/recipe_data/aafa8b5e16f64053a74ea344dfb16252.recipe')
    r.print_recipe()
    test = RecipeDB()
    test.create_database()
    test.add(r)
