"""
    pyreicpe.db
    ~~~~~~~~~~~

    The main database connection file for pyrecipe. This module handles
    the connection, query, and building of the database.
"""
import os
import sys
import sqlite3

import pyrecipe.utils as utils
from pyrecipe.backend.recipe import Recipe
from pyrecipe import p


if not os.path.isdir(os.path.expanduser("~/.local/share/pyrecipe")):
    os.makedirs(os.path.expanduser("~/.local/share/pyrecipe"))

if sys.base_prefix == sys.prefix:
    DB_FILE = os.path.expanduser("~/.local/share/pyrecipe/recipes.db")
else:
    DB_FILE = os.path.expanduser("~/Code/pyrecipe/pyrecipe/backend/recipes.db")

DB_DIR = os.path.dirname(os.path.realpath(__file__))


class RecipeNotFound(Exception):
    pass


class RecipeAlreadyStored(Exception):
    pass


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


    def _get_dict_from_row(self, row):
        return dict(zip(row.keys(), row))


    def _insert_ingredient(self, ingred):
        """Inserts ingredients data into the database"""

        self.c.execute(
            "INSERT OR IGNORE INTO Ingredients(name) VALUES(?)",
               (ingred.name,)
        )
        self.c.execute(
            "INSERT OR IGNORE INTO Units(unit) VALUES(?)",
               (str(ingred.unit),)
        )
        
        if ingred.size:
            self.c.execute(
                "INSERT OR IGNORE INTO IngredientSizes(ingredient_size) VALUES(?)",
                   (str(ingred.size),)
            )
        
        if ingred.prep:
            self.c.execute(
                "INSERT OR IGNORE INTO IngredientPrep(prep) VALUES(?)",
                   (str(ingred.prep),)
            )

    
    def _get_recipe_ingredients(self, recipe_id):
        self.c.execute(
            '''SELECT recipe_ingredient_id, amount, ingredient_size, name, unit, prep
               FROM RecipeIngredients AS ri
               LEFT JOIN IngredientSizes AS isi ON ri.size_id=isi.id
               INNER JOIN Units AS u ON ri.unit_id=u.id
               INNER JOIN Ingredients AS i ON ri.ingredient_id=i.id
               LEFT JOIN IngredientPrep AS ip ON ri.prep_id=ip.id
               WHERE recipe_id=?''', (recipe_id,)
        )
        
        ingred_rows = self.c.fetchall()
        ingred_list = []
        for item in ingred_rows:
            ingredient = self._get_dict_from_row(item)
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
            alt_name = self._get_dict_from_row(item)['alt_name']
            self.c.execute(
                '''SELECT recipe_ingredient_id, amount, ingredient_size, name, unit, prep
                   FROM NamedIngredients AS ni
                   INNER JOIN NamedIngredientsNames
                       AS nin ON ni.named_ingredient_id=nin.id
                   LEFT JOIN IngredientSizes AS isi ON ni.size_id=isi.id
                   INNER JOIN Units AS u ON ni.unit_id=u.id
                   INNER JOIN Ingredients AS i ON ni.ingredient_id=i.id
                   LEFT JOIN IngredientPrep AS ip ON ni.ingredient_id=ip.id
                   WHERE ni.recipe_id=? AND alt_name=?''', (recipe_id, alt_name)
            )
            named_ingred_rows = self.c.fetchall()
            ingredients = []
            for item in named_ingred_rows:
                ingredient = self._get_dict_from_row(item)
                ingredients.append(ingredient)
            ingred_list[alt_name] = ingredients
        return ingred_list


    def create_recipe(self, recipe):
        '''Add a recipe to the database.'''
        self.c.execute(
            '''SELECT name FROM Recipes
               WHERE name=?''', (recipe.name,)
        )
        if self.c.fetchone():
            msg = ("A recipe with the name '{}' already exists in the "
                   "database. Please Select another name for this "
                   "recipe.".format(recipe.name))
            raise RecipeAlreadyStored(utils.msg(msg, 'ERROR'))

        recipe_data = [(
            recipe.uuid, 
            recipe.name.lower(),
            recipe.dishtype,
            recipe.author,
            recipe.tags,
            recipe.categories,
            recipe.price,
            recipe.url
        )]

        self.c.executemany(
            '''INSERT OR IGNORE INTO Recipes (
                uuid,
                name,
                dishtype,
                author,
                tags,
                categories,
                price,
                url
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
            
            self.c.execute(
                '''SELECT id 
                   FROM IngredientSizes
                   WHERE ingredient_size=?''',
                   (item.size,)
            )
            try:
                ingredient_size_id = self.c.fetchone()['id']
            except TypeError:
                ingredient_size_id = None
            
            self.c.execute(
                '''SELECT id 
                   FROM IngredientPrep
                   WHERE prep=?''',
                   (item.prep,)
            )
            
            try:
                prep_id = self.c.fetchone()['id']
            except TypeError:
                prep_id = None
            
            self.c.execute(
                '''INSERT OR IGNORE
                   INTO RecipeIngredients 
                   (recipe_id, 
                    amount, 
                    size_id, 
                    unit_id, 
                    ingredient_id,
                    prep_id
                    ) VALUES(?, ?, ?, ?, ?, ?)''', 
                    (recipe_id, 
                     str(item.amount), 
                     ingredient_size_id,
                     int(unit_id), 
                     int(ingredient_id),
                     prep_id)
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
                alt_name_id = self._get_dict_from_row(self.c.fetchone())['id']

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
                            '''SELECT id 
                               FROM IngredientSizes
                               WHERE ingredient_size=?''',
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
                '''INSERT OR REPLACE INTO RecipeSteps (
                    recipe_id,
                    step
                    ) VALUES(?, ?)
                ''', (recipe_id, item['step'])
            )

        self.conn.commit()


    def read_recipe(self, name):
        self.c.execute("SELECT * FROM Recipes WHERE name=?", (name,))
        row = self.c.fetchone()
        if row:
            row = self._get_dict_from_row(row)
            recipe = Recipe(row)
        else:
            msg = '"{}" was not found in the database.'.format(name)
            return RecipeNotFound(utils.msg(msg, 'ERROR'))
        
        recipe.ingredients = self._get_recipe_ingredients(recipe.id)

        test = []
        named_ingredients = self._get_recipe_named_ingredients(recipe.id)
        for k, v in named_ingredients.items():
            test.append({k: v})

        if named_ingredients:
            recipe.named_ingredients = test

        self.c.execute(
            '''SELECT step
               FROM RecipeSteps
               WHERE recipe_id=?''', (recipe.id,)
        )

        step_rows = self.c.fetchall()
        step_list = []
        for item in step_rows:
            step = self._get_dict_from_row(item)
            step_list.append(step)

        recipe.steps = step_list
        return recipe


    def update_recipe(self, recipe):
        '''Update a recipe in the database.'''
        recipe_data = [(
            recipe.name,
            recipe.dishtype,
            recipe.author,
            recipe.tags,
            recipe.categories,
            recipe.price,
            recipe.url,
            recipe.id
        )]

        self.c.executemany(
            '''UPDATE Recipes
               SET
                name=?,
                dishtype=?,
                author=?,
                tags=?,
                categories=?,
                price=?,
                url=?
               WHERE id=?''', recipe_data
        )
        
        ingreds, named = recipe.get_ingredients()
        for item in ingreds:
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
            
            self.c.execute(
                '''SELECT id 
                   FROM IngredientSizes
                   WHERE ingredient_size=?''',
                   (item.size,)
            )
            try:
                ingredient_size_id = self.c.fetchone()['id']
            except TypeError:
                ingredient_size_id = None
            
            self.c.execute(
                '''SELECT id 
                   FROM IngredientPrep
                   WHERE prep=?''',
                   (item.prep,)
            )
            
            try:
                prep_id = self.c.fetchone()['id']
            except TypeError:
                prep_id = None
            if item.id:
                self.c.execute(
                    '''UPDATE RecipeIngredients
                       SET
                        amount=?,
                        size_id=?,
                        unit_id=?,
                        ingredient_id=?,
                        prep_id=?
                       WHERE recipe_ingredient_id=?''',
                       (str(item.amount),
                        ingredient_size_id,
                        int(unit_id),
                        int(ingredient_id),
                        prep_id,
                        item.id)
                )
            else:
                self.c.execute(
                    '''INSERT into RecipeIngredients(
                        recipe_id,
                        amount, 
                        size_id, 
                        unit_id, 
                        ingredient_id,
                        prep_id)
                       VALUES(?, ?, ?, ?, ?, ?)''',
                       (recipe.id,
                        str(item.amount), 
                        ingredient_size_id,
                        int(unit_id), 
                        int(ingredient_id),
                        prep_id)
                )

    
        if named:
            for item, ingreds in named.items():
                self.c.execute(
                    '''INSERT OR IGNORE INTO NamedIngredientsNames (
                            recipe_id,
                            alt_name
                            ) VALUES(?, ?)''',
                            (recipe.id,
                             item)
                )
                self.c.execute(
                    '''SELECT id FROM NamedIngredientsNames
                       WHERE alt_name=?''', (item,)
                )
                alt_name_id = self._get_dict_from_row(self.c.fetchone())['id']

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
                            '''SELECT id 
                               FROM IngredientSizes
                               WHERE ingredient_size=?''',
                               (ingred.size,)
                        )

                    if ingred.id:

                        self.c.execute(
                            '''UPDATE NamedIngredients
                               SET
                                amount=?,
                                size_id=?,
                                unit_id=?,
                                ingredient_id=?,
                                prep_id=?
                               WHERE recipe_ingredient_id=?''',
                               (str(ingred.amount),
                                ingredient_size_id,
                                int(unit_id),
                                int(ingredient_id),
                                prep_id,
                                ingred.id)
                        )
                    else:
                        self.c.execute(
                            '''INSERT into NamedIngredients(
                                recipe_id,
                                amount, 
                                size_id, 
                                unit_id, 
                                ingredient_id,
                                prep_id)
                               VALUES(?, ?, ?, ?, ?, ?)''',
                               (recipe.id,
                                str(ingred.amount), 
                                ingredient_size_id,
                                int(unit_id), 
                                int(ingredient_id),
                                prep_id)
                        )

        #for item in recipe.steps:
        #    self.c.execute(
        #        '''INSERT OR IGNORE INTO RecipeSteps (
        #            recipe_id,
        #            step
        #            ) VALUES(?, ?)
        #        ''', (recipe.id, item['step'])
        #    )

        self.conn.commit()
    

    def delete_recipe(self, name):
        """Delete recipe from database."""
        self.c.execute(
                "DELETE FROM Recipes WHERE name=?",
                (name,)
        )
        self.conn.commit()


    def __del__(self):
        self.conn.close()


    def create_database(self):
        """Create the recipe database."""
        tables = os.path.join(DB_DIR, "tables.sql")
        with open(tables) as fi:
            self.c.executescript(fi.read())


class DBInfo(RecipeDB):
    """Get data from the database as a dict."""
    
    def get_recipes(self):
        """Return all of the recipe names in the database."""
        names = self.c.execute("SELECT name FROM Recipes")
        names = [x[0] for x in names]
        return names
    
    def get_recipes_by_dishtype(self, dishtype):
        """Get recipenames of a cirtain dishtype.""" 
        names = self.query(
            "SELECT name FROM Recipes WHERE dishtype = \'{}\'".format(dishtype)
        )
        names = [x[0] for x in names]
        return names
    
    def get_recipes_by_author(self, author):
        """Get recipenames of a cirtain dishtype.""" 
        names = self.c.execute(
            "SELECT name FROM Recipes WHERE author = \'{}\'".format(author)
        )
        names = [x[0] for x in names]
        return names
    
    def get_uuid(self, name):
        """Get the uuid of the recipe."""
        uuid = self.query(
            "SELECT recipe_uuid FROM recipes WHERE name = \'{}\' COLLATE NOCASE".format(name)
        )
        if uuid:
            return uuid[0][0]
        return None

    @property
    def words(self):
        """A complete list of searchable words from the database."""
        words = []
        results = []
        queries = [
            'SELECT * FROM recipesearch',
            'SELECT * FROM ingredientsearch'
        ]
        for query in queries:
            results += self.query(query)
        for w in results:
            # Get rid of empty strings
            w = [i for i in w if i]
            # Split words at spaces 
            w = [w for s in w for w in s.split()]
            words += w
        return set(words)
    
    def search(self, args=[]):
        """Search the database."""
        arg_list = []
        for arg in args:
            arg_list += arg.split()
        arg_list += [p.plural(w) for w in arg_list] 
        queries = [
            'SELECT name FROM recipesearch WHERE recipesearch MATCH "{}"',
            'SELECT name FROM ingredientsearch WHERE ingredientsearch MATCH "{}"'
        ]
        results = []
        for string in arg_list:
            for query in queries:
                result = self.query(query.format(string))
                result = [i[0] for i in result]
                results += result
        return set(results)


if __name__ == '__main__':
    db = RecipeDB()
    recipe = db.read_recipe('pesto')
    print(recipe.__dict__)
