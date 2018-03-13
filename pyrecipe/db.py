import os
import sqlite3
import pickle

from pyrecipe.config import DB_FILE
from pyrecipe.recipe import Recipe
from pyrecipe.utils import manifest


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
        for item in recipe.get_ingredients():
            self.c.execute('''INSERT INTO RecipeIngredients (
                                recipe_id, 
                                ingredient_str
                                ) VALUES(?, ?)''', (recipe_id, item)) 
        self._commit()


    def __del__(self):
        self.conn.close()
        #print('DATABASE CLOSED')

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
        self.c.execute('''CREATE TABLE Recipes 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                          dish_type TEXT,
                          name TEXT, 
                          file_name TEXT, 
                          author TEXT, 
                          tags TEXT, 
                          categories TEXT, 
                          price TEXT, 
                          source_url TEXT
                          )''')
        
        self.c.execute('''CREATE TABLE RecipeIngredients 
                          (
                           recipe_id INTEGER, 
                           ingredient_str TEXT,
                           FOREIGN KEY(recipe_id) REFERENCES Recipes(id)
                          )''')

def get_names():
    db = RecipeDB()
    #r = Recipe('pesto')
    sql = 'SELECT name FROM Recipes'
    names = db.query(sql)
    name_list = []
    for item in sorted(names):
        #name = "'{}'".format(item[0].lower())
        name = item[0].lower()
        name_list.append(name)
    for item in name_list:
        pass
        #print(item)
    return name_list

if not os.path.exists(DB_FILE):
    db = RecipeDB()
    db.build_database()
    names = manifest.recipe_names
    for item in names:
        r = Recipe(item)
        db.add_recipe(r)

if __name__ == '__main__':
    names = get_names()
    with open('test.p', 'wb') as fi:
        pickle.dump(names, fi)
    for item in names:
        print(item)

