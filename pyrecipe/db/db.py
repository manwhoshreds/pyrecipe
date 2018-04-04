"""
    pyreicpe.db
    ~~~~~~~~~~~
    
    The main database file for pyrecipe.
"""
import os
import sqlite3

DB_FILE = os.path.expanduser('~/.conifg/pyrecipe/recipes.db')

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
        if type(recipe).__name__ != 'Recipe':
            raise TypeError('Argument must be a Recipe instance, not {}'
                            .format(type(recipe)))

        recipe_data = [(
            recipe['recipe_uuid'],
            recipe['recipe_name'].lower(),
            recipe['dish_type'],
            recipe['author'],
            recipe['tags'],
            recipe['categories'],
            recipe['price'],
            recipe['source_url']
        )]
        self.c.executemany(
            '''INSERT OR REPLACE INTO Recipes (
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
        self._commit()
        #self.c.execute("SELECT id FROM Recipes WHERE name = '%s'" % recipe['recipe_name'])
        #recipe_id = self.c.fetchone()[0]
        #for item in recipe.get_ingredients()[0]:
        #    self.c.execute('''INSERT OR REPLACE INTO RecipeIngredients (
        #                        recipe_id, 
        #                        ingredient_str
        #                        ) VALUES(?, ?)''', (recipe_id, item)) 
        #self._commit()
        
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
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS Recipes 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              recipe_uuid TEXT NOT NULL, 
              dish_type TEXT,
              name TEXT NOT NULL, 
              author TEXT, 
              tags TEXT, 
              categories TEXT, 
              price TEXT, 
              source_url TEXT,
              CONSTRAINT unique_name UNIQUE
              (name, recipe_uuid)
              )'''
        )
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS RecipeIngredients 
              (
               recipe_id INTEGER, 
               ingredient_str TEXT,
               FOREIGN KEY(recipe_id) REFERENCES Recipes(id)
              )'''
        )
        self.c.execute(
            '''CREATE TABLE IF NOT EXISTS RecipeAltIngredients
              (
               recipe_id INTEGER,
               alt_name TEXT,
               ingredient_str TEXT,
               FOREIGN KEY(recipe_id) REFERENCES Recipes(id)
              )'''
        )

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
            sql = "DELETE FROM Recipes WHERE recipe_uuid = \'{}\'".format(deleted_file)
            db.execute(sql)
    return wrapper

if __name__ == '__main__':
    pass
