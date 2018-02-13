
import os
import sqlite3

from pyrecipe.config import DB_FILE
from pyrecipe.recipe import Recipe
from pyrecipe import manifest
from birdseye import eye


class RecipeDB:
    """A database subclass for pyrecipe"""
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.c = self.conn.cursor()

    def add_recipe(self, recipe):
        '''must take in a reicpe instance'''
        if not isinstance(recipe, Recipe):
            raise TypeError('Argument must be a Recipe instance, not {}'
                            .format(type(recipe)))

        recipe_data = [(
                       recipe['recipe_name'],
                       recipe['dish_type'],
                       recipe['source'],
                       recipe['author'],
                       recipe['tags'],
                       recipe['categories'],
                       recipe['price'],
                       recipe['source_url']

                    )]
        self.c.executemany('''INSERT INTO Recipes (name, dish_type, file_name, author, tags, categories, price, source_url)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?)''', recipe_data)
        self._commit()
        
        self.c.execute("SELECT id FROM Recipes WHERE name = '%s'" % recipe['recipe_name'])
        recipe_id = self.c.fetchone()[0]
        for item in recipe.get_ingredients():
            self.c.execute('''INSERT INTO RecipeIngredients (recipe_id, ingredient_str) VALUES(?, ?)''', (recipe_id, item)) 
        self._commit()


    def __del__(self):
        self.conn.close()

    def _commit(self):
        self.conn.commit()

    def execute(self, command):
        return self.c.execute(command)

    def build_database(self):
        self.c.execute('''CREATE TABLE Recipes (id INTEGER PRIMARY KEY AUTOINCREMENT, dish_type TEXT,
                          name TEXT, file_name TEXT, author TEXT, tags TEXT, categories TEXT, price TEXT, 
                          source_url TEXT)''')
        self.c.execute('''CREATE TABLE RecipeIngredients (recipe_id INTEGER, ingredient_str TEXT)''')



if not os.path.exists(DB_FILE):
    db = RecipeDB()
    db.build_database()
    names = manifest.recipe_names
    for item in names:
        r = Recipe(item)
        db.add_recipe(r)

if __name__ == '__main__':
    db = RecipeDB()
    r = Recipe('pesto')
    test = db.execute("SELECT name FROM Recipes WHERE dish_type = 'main'")
    db.add_recipe(r)
