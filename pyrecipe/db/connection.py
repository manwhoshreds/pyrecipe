"""
    pyreicpe.db
    ~~~~~~~~~~~

    The main database connection file for pyrecipe. This module handles
    the connection, query, and building of the database.
"""
import os
import sqlite3

from pyrecipe.recipe import Recipe


if not os.path.isdir(os.path.expanduser("~/.local/share/pyrecipe")):
    os.makedirs(os.path.expanduser("~/.local/share/pyrecipe"))
DB_FILE = os.path.expanduser("~/.local/share/pyrecipe/recipes.db")
TABLES = os.path.abspath("tables.sql")

def read_sql():
    with open(TABLES) as fi:
        commands = fi.read().split(';')

    return commands
        
def get_dict_from_row(row):
    return dict(zip(row.keys(), row))

class RecipeDB:
    """A database class for pyrecipe."""
    def __init__(self):
        try:
            self.conn = sqlite3.connect(DB_FILE)
        except sqlite3.OperationalError:
            sys.exit('Something unexpected happened....')
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()
        self.c.execute("PRAGMA foreign_keys = ON")
    

    def _insert_ingredient(self, ingred):
        """Inserts ingredients data into the database"""
        
        self.c.execute(
            "INSERT OR IGNORE INTO Ingredients (name) VALUES(?)",
               (ingred.name,)
        )
        self.c.execute(
            "INSERT OR IGNORE INTO Units (unit) VALUES(?)",
               (str(ingred.unit),)
        )
        self.c.execute(
            "INSERT OR IGNORE INTO IngredientSizes (sizee) VALUES(?)",
               (str(ingred.size),)
        )
        self.c.execute(
            '''SELECT id FROM Ingredients
               WHERE name=?''',
               (ingred.name,)
        )
        
        ingredient_size_id = None
        if ingred.size:
            ingredient_size_id = self.c.execute(
                '''SELECT id 
                   FROM IngredientSizes
                   WHERE sizee=?''',
                   (ingred.size,)
            )

    def add(self, recipe):
        '''Add a recipe to the database.'''
        
        self.c.execute(
            '''SELECT name FROM Recipes
               WHERE name=?''', (recipe.name.lower(),)
        )
        if self.c.fetchone():
            #pass
            return

        recipe_data = [(
            recipe.uuid,
            recipe.name.lower(),
            recipe.dish_type,
            recipe.author,
            recipe.tags,
            recipe.categories,
            recipe.price,
            recipe.source_url
        )]
        
        self.c.executemany(
            '''INSERT OR IGNORE INTO recipes (
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
        
        self.c.execute(
            "SELECT id FROM recipes WHERE name=?",
            (recipe.name.lower(),)
        )
        
        recipe_id = self.c.fetchone()['id']
        
        for item in recipe.get_ingredients()[0]:
            self._insert_ingredient(item)
            
            self.c.execute(
                '''SELECT id FROM Ingredients
                   WHERE name=?''',
                   (item.name,)
            )
            
            ingredient_id = self.c.fetchone()['id']
            
            self.c.execute(
                '''SELECT id FROM Units
                   WHERE unit=?''',
                   (item.unit,)
            )

            unit_id = self.c.fetchone()['id']
            
            ingredient_size_id = 2
            if item.size:
                ingredient_size_id = self.c.execute(
                    '''SELECT id 
                       FROM IngredientSizes
                       WHERE sizee=?''',
                       (item.size,)
                )
                test = self.c.fetchone()
            print(ingredient_size_id) 
            self.c.execute(
                '''INSERT OR IGNORE
                   INTO RecipeIngredients 
                   (recipe_id,
                    amount,
                    size_id,
                    unit_id,
                    ingredient_id
                    ) VALUES(?, ?, ?, ?, ?)''', 
                    (recipe_id, 
                    str(item.amount),
                    int(ingredient_size_id),
                    int(unit_id),
                    int(ingredient_id))
            )
    
        if recipe.get_ingredients()[1]:
            for item, ingreds in recipe.get_ingredients()[1].items():
                self.c.execute(
                    '''INSERT OR IGNORE INTO NamedIngredientsNames (
                            recipe_id,
                            alt_name
                            ) VALUES(?, ?)''',
                            (recipe_id,
                             item)
                )
                self.c.execute(
                    '''SELECT id FROM NamedIngredientsNames
                       WHERE alt_name=?''', (item,)
                )
                alt_name_id = get_dict_from_row(self.c.fetchone())['id']
                       
                for ingred in ingreds:
                    self._insert_ingredient(ingred)
                    
                    self.c.execute(
                        '''SELECT id FROM Ingredients
                           WHERE name=?''',
                           (ingred.name,)
                    )
                    
                    ingredient_id = self.c.fetchone()['id']
                    
                    self.c.execute(
                        '''SELECT id FROM Units
                           WHERE unit=?''',
                           (ingred.unit,)
                    )

                    unit_id = self.c.fetchone()['id']
                    
                    ingredient_size_id = None
                    if ingred.size:
                        ingredient_size_id = self.c.execute(
                            '''SELECT ingredient_size_id 
                               FROM IngredientSizes
                               WHERE ingredient_size_id=?''',
                               (ingred.size,)
                        )

                    self.c.execute(
                        '''INSERT OR REPLACE INTO NamedIngredients (
                                recipe_id,
                                named_ingredient_id,
                                amount,
                                size_id,
                                unit_id,
                                ingredient_id
                                ) VALUES(?, ?, ?, ?, ?, ?)''', 
                                (recipe_id,
                                 alt_name_id,
                                 str(ingred.amount),
                                 ingredient_size_id,
                                 int(unit_id),
                                 int(ingredient_id))
                    )
        
        for item in recipe.steps:
            self.c.execute(
                '''INSERT OR IGNORE INTO RecipeSteps (
                    recipe_id,
                    step
                    ) VALUES(?, ?)
                ''', (recipe_id, item['step'])
            )

        self._commit()

    
    def _get_recipe_ingredients(self, recipe_id):
        self.c.execute(
            '''SELECT amount, unit, name
               FROM RecipeIngredients AS ri
               INNER JOIN IngredientSizes AS isi ON ri.size_id=isi.id
               INNER JOIN Units AS u ON ri.unit_id=u.id
               INNER JOIN Ingredients AS i ON ri.ingredient_id=i.id
               WHERE recipe_id=?''', (recipe_id,)
        )
        ingred_rows = self.c.fetchall()
        
        ingred_list = []
        for item in ingred_rows:
            ingredient = get_dict_from_row(item)
            ingred_list.append(ingredient)
        return ingred_list
    
    def _get_recipe_named_ingredients(self, recipe_id):
        self.c.execute(
            '''SELECT alt_name 
               FROM NamedIngredientsNames
               WHERE recipe_id=?''', (recipe_id,)
        )
        alt_names = self.c.fetchall()
        ingred_list = {}
        for item in alt_names:
            alt_name = get_dict_from_row(item)['alt_name']
            self.c.execute(
                '''SELECT amount, unit, name
                   FROM NamedIngredients AS ni
                   INNER JOIN NamedIngredientsNames 
                       AS nin ON ni.named_ingredient_id=nin.id
                       --AS nin ON ni.recipe_id=nin.recipe_id
                   INNER JOIN IngredientSizes AS isi ON ni.size_id=isi.id
                   INNER JOIN Units AS u ON ni.unit_id=u.id
                   INNER JOIN Ingredients AS i ON ni.ingredient_id=i.id
                   WHERE ni.recipe_id=? AND alt_name=?''', (recipe_id, alt_name)
            )
            named_ingred_rows = self.c.fetchall()
            ingredients = []
            for item in named_ingred_rows:
                ingredient = get_dict_from_row(item)
                ingredients.append(ingredient)
            ingred_list[alt_name] = ingredients
        return ingred_list

    
    def get_recipe(self, recipe):
        self.c.execute("SELECT * FROM Recipes WHERE name=\'{}\'".format(recipe))
        row = self.c.fetchone()     
        if row:
            recipe_data = get_dict_from_row(row)
        else:
            exit("No recipe found by the name of {}".format(recipe))
        
        ingredients = self._get_recipe_ingredients(recipe_data['id'])
        recipe_data['ingredients'] = ingredients

        test = []
        named_ingredients = self._get_recipe_named_ingredients(recipe_data['id'])
        for k, v in named_ingredients.items():
            test.append({k: v})
        
        if named_ingredients:
            recipe_data['named_ingredients'] = test

        self.c.execute(
            '''SELECT step 
               FROM RecipeSteps
               WHERE recipe_id=?''', (recipe_data['id'],)
        )
        
        step_rows = self.c.fetchall()
        step_list = []
        for item in step_rows:
            step = get_dict_from_row(item)
            step_list.append(step)

        recipe_data['steps'] = step_list


        return recipe_data

    
    def __del__(self):
        self.conn.close()

    
    def _commit(self):
        self.conn.commit()

    
    def create_database(self):
        """Create the recipe database."""
        for command in read_sql():
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
    import sys
    import os
    print(__global__)
    test = RecipeDB()
    test.create_database()
    base_path = '/home/michael/.config/pyrecipe/recipe_data/'
    recipes = os.listdir(base_path)
    for item in recipes:
        fil = os.path.join(base_path, item)
        r = Recipe(fil)
        test.add(r)
    what = test.get_recipe(sys.argv[1])
    print(what)
    r = Recipe(what)
    r.print_recipe()


