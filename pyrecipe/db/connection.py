"""
    pyreicpe.db
    ~~~~~~~~~~~

    The main database connection file for pyrecipe. This module handles
    the connection, query, and building of the database.
"""
import os
import sqlite3

from pyrecipe.config import DB_FILE

TABLES = {}
TABLES['recipesearch'] = """
    CREATE VIRTUAL TABLE {0}
    USING FTS5(name, author, tags, categories)
"""
TABLES['ingredientsearch'] = """
    CREATE VIRTUAL TABLE {0}
    USING FTS5(name, ingredient)
"""
TABLES['recipes'] = """
    CREATE TABLE IF NOT EXISTS {0}(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipe_uuid TEXT NOT NULL UNIQUE,
        dish_type TEXT,
        name TEXT NOT NULL UNIQUE,
        author TEXT,
        tags TEXT,
        categories TEXT,
        price TEXT,
        source_url TEXT)
"""
TABLES['ingredients'] = """
    CREATE TABLE IF NOT EXISTS {0}(
        recipe_id INTEGER,
        ingredient_str TEXT,
        CONSTRAINT fk_ingredients
            FOREIGN KEY(recipe_id)
            REFERENCES Recipes(id)
            ON DELETE CASCADE)
"""
TABLES['named_ingredients'] = """
    CREATE TABLE IF NOT EXISTS {0}(
        recipe_id INTEGER,
        alt_name TEXT,
        ingredient_str TEXT,
        FOREIGN KEY(recipe_id)
        REFERENCES Recipes(id))
"""
TABLES['steps'] = """
    CREATE TABLE IF NOT EXISTS {0}(
        recipe_id INTEGER,
        step TEXT,
        FOREIGN KEY(recipe_id) 
        REFERENCES Recipes(id))
"""

class RecipeDB:
    """A database subclass for pyrecipe."""
    def __init__(self):
        try:
            self.conn = sqlite3.connect(DB_FILE)
        except sqlite3.OperationalError:
            sys.exit('Something unexpected happened....')
        self.c = self.conn.cursor()
        self.c.execute("PRAGMA foreign_keys = ON")

    def add_recipe(self, recipe):
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
        self.c.executemany(
            '''INSERT OR REPLACE INTO recipesearch (
                name,
                author,
                tags,
                categories
                ) VALUES(?, ?, ?, ?)''', recipe_data_search
        )
        for ingredient in recipe.ingredients:
            ingredient_data_search = [(
                recipe.name,
                ingredient.name
            )]
            self.c.executemany(
                '''INSERT OR REPLACE INTO ingredientsearch (
                    name,
                    ingredient
                    ) VALUES(?, ?)''', ingredient_data_search
            )
        self._commit()
        recipe_id = self.query(
            "SELECT id FROM recipes WHERE name = \'{}\'"
            .format(recipe.name)
        )
        for item in recipe.get_ingredients(fmt='string')[0]:
            self.c.execute('''INSERT OR REPLACE INTO ingredients (
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
        for name, statement in TABLES.items():
            self.c.execute(statement.format(name))

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
    r = Recipe('zesty meatloaf')
    print(r.get_ingredients())
    if r.get_ingredients(fmt='string')[1]:
        print("yea baw thats it ")
    
    for item, ingreds in r.get_ingredients(fmt='string')[1].items():
        for test in ingreds:
            print(item, test)
        


