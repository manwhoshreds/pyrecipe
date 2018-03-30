"""
    pyreicpe.db
    ~~~~~~~~~~~
    
    The main database file for pyrecipe.
"""
import os
import sqlite3

from pyrecipe import Recipe
from pyrecipe.config import DB_FILE, RECIPE_DATA_FILES


class RecipeDB:
    """A database subclass for pyrecipe."""
    def __init__(self):
        try: 
            self.conn = sqlite3.connect(DB_FILE)
        except sqlite3.OperationalError:
            sys.exit('Something unexpected happened....')
        self.c = self.conn.cursor()

    def add_recipe(self, recipe):
        '''Add a recipe to the database.'''
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
        for item in recipe.get_ingredients()[0]:
            self.c.execute('''INSERT INTO RecipeIngredients (
                                recipe_id, 
                                ingredient_str
                                ) VALUES(?, ?)''', (recipe_id, item)) 
        self._commit()


    def __del__(self):
        self.conn.close()

    def _commit(self):
        self.conn.commit()

    def execute(self, command):
        return self.c.execute(command)

    def query(self, command):
        if not command.lower().startswith('select'):
            raise TypeError('query string must be one of select')
        query = self.c.execute(command)
        result = query.fetchall()
        return result
    
    def build_database(self):
        self.c.execute(
            '''CREATE TABLE Recipes 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              dish_type TEXT,
              name TEXT NOT NULL, 
              file_name TEXT NOT NULL, 
              author TEXT, 
              tags TEXT, 
              categories TEXT, 
              price TEXT, 
              source_url TEXT,
              CONSTRAINT unique_name UNIQUE
              (name, file_name)
              )'''
        )
        self.c.execute(
            '''CREATE TABLE RecipeIngredients 
              (
               recipe_id INTEGER, 
               ingredient_str TEXT,
               FOREIGN KEY(recipe_id) REFERENCES Recipes(id)
              )'''
        )

class Manifest():
    """A record of all of recipe types in the database."""
    def __init__(self):
        db = RecipeDB()
        disht_sql = "SELECT name FROM Recipes WHERE dish_type = \'%s\'"
        recipe_names = db.query('SELECT name FROM Recipes')
        main_dishes = db.query(disht_sql % 'main')
        salad_dressings = db.query(disht_sql % 'salad dressing')
        
        self.main_dishes = [x[0] for x in main_dishes]
        self.salad_dressings = [x[0] for x in salad_dressings]
        self.recipe_names = sorted([x[0].lower() for x in recipe_names])

def update_db(save_recipe):
    """Decorater for updating pyrecipe db."""
    def wrapper(recipe):
        save_recipe()
    return wrapper

if not os.path.exists(DB_FILE):
    db = RecipeDB()
    db.build_database()
    for item in RECIPE_DATA_FILES:
        r = Recipe(item)
        db.add_recipe(r)

if __name__ == '__main__':
    test = Manifest()
    print(test.recipe_names)
