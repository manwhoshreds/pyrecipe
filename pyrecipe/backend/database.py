"""
    pyreicpe.db
    ~~~~~~~~~~~

    The main database connection file for pyrecipe. This module handles
    the connection, query, and building of the database.
"""
import os
import sys
import sqlite3
from itertools import zip_longest

import pyrecipe.utils as utils
#from pyrecipe import p


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
            '''SELECT group_name FROM IngredientGroups
               WHERE group_name=?''', (ingred.group_name,)
        )
        if not self.c.fetchone():
            if ingred.group_name:
                self.c.execute(
                    "INSERT OR IGNORE INTO IngredientGroups(group_name) VALUES(?)",
                       (ingred.group_name,)
                )
        
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
            '''SELECT 
                recipe_ingredient_id,
                group_name, 
                amount, 
                ingredient_size, 
                name, 
                unit, 
                prep
               FROM RecipeIngredients AS ri
               LEFT JOIN IngredientGroups as ig 
                    ON ri.group_id=ig.id
               LEFT JOIN IngredientSizes AS isi 
                    ON ri.size_id=isi.id
               INNER JOIN Units AS u 
                    ON ri.unit_id=u.id
               INNER JOIN Ingredients AS i 
                    ON ri.ingredient_id=i.id
               LEFT JOIN IngredientPrep AS ip 
                    ON ri.prep_id=ip.id
               WHERE recipe_id=?''', (recipe_id,)
        )
        
        ingred_rows = self.c.fetchall()
        ingred_list = []
        for item in ingred_rows:
            ingredient = self._get_dict_from_row(item)
            ingred_list.append(ingredient)
        return ingred_list
    
    @property
    def recipes(self):
        '''Return a list of all recipes in the database'''
        self.c.execute(
            '''SELECT name FROM Recipes'''
        )
        recipes = []
        for item in self.c.fetchall():
            recipes.append(self._get_dict_from_row(item)['name'])
        return recipes
    
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
            recipe.dish_type,
            recipe.author,
            recipe.source_url,
            recipe.prep_time,
            recipe.cook_time
        )]

        self.c.executemany(
            '''INSERT OR IGNORE INTO Recipes (
                uuid,
                name,
                dish_type,
                author,
                source_url,
                prep_time,
                cook_time
                ) VALUES(?, ?, ?, ?, ?, ?, ?)''', recipe_data
        )

        self.c.execute(
            "SELECT recipe_id FROM recipes WHERE name=?",
            (recipe.name.lower(),)
        )
        recipe_id = self.c.fetchone()['recipe_id']

        for item in recipe.ingredients:
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
                '''SELECT id
                   FROM IngredientGroups
                   WHERE group_name=?''',
                   (item.group_name,)
            )
            try: 
                group_id = self.c.fetchone()['id']
            except TypeError:
                group_id = None
            
            self.c.execute(
                '''INSERT OR IGNORE
                   INTO RecipeIngredients 
                   (recipe_id, 
                    group_id,
                    amount, 
                    size_id, 
                    unit_id, 
                    ingredient_id,
                    prep_id
                    ) VALUES(?, ?, ?, ?, ?, ?, ?)''', 
                    (recipe_id,
                     group_id,
                     str(item.amount), 
                     ingredient_size_id,
                     int(unit_id), 
                     int(ingredient_id),
                     prep_id)
            )
    
        
        for item in recipe.steps:
            try:
                #temp fix for reading from file
                step = item['step']
            except TypeError:
                step = item
            
            self.c.execute(
                '''INSERT OR REPLACE INTO RecipeSteps (
                    recipe_id,
                    step
                    ) VALUES(?, ?)
                ''', (recipe_id, step)
            )

        
        recipe.notes = ['Add note.']
        for note in recipe.notes:
            self.c.execute(
                '''INSERT OR REPLACE INTO RecipeNotes (
                    recipe_id,
                    note
                    ) VALUES(?, ?)
                ''', (recipe_id, note)
            )
        
        self.conn.commit()

    def read_recipe(self, recipe):
        self.c.execute("SELECT * FROM Recipes WHERE name=?", (recipe.name,))
        row = self.c.fetchone()
        if row:
            row = self._get_dict_from_row(row)
            recipe._set_data(row)
        else:
            raise RecipeNotFound()
        
        recipe.ingredients = self._get_recipe_ingredients(recipe.recipe_id)

        self.c.execute(
            '''SELECT id, step
               FROM RecipeSteps
               WHERE recipe_id=?''', (recipe.recipe_id,)
        )

        step_rows = self.c.fetchall()
        step_list = []
        for item in step_rows:
            step = self._get_dict_from_row(item)
            step_list.append(step['step'])
        recipe.steps = step_list
        
        self.c.execute(
            '''SELECT id, note
               FROM RecipeNotes
               WHERE recipe_id=?''', (recipe.recipe_id,)
        )
        
        note_rows = self.c.fetchall()
        note_list = []
        for item in note_rows:
            note = self._get_dict_from_row(item)
            note_list.append(note['note'])
        recipe.notes = note_list
        return recipe

    
    def _get_step_ids(self, recipe_id):
        self.c.execute(
            '''SELECT id
               FROM RecipeSteps
               WHERE recipe_id=?''', (recipe_id,)
        )
        step_ids = self.c.fetchall()
        ids = []
        for item in step_ids:
            ids.append(self._get_dict_from_row(item)['id'])
        return ids

    def _get_note_ids(self, recipe_id):
        self.c.execute(
            '''SELECT id
               FROM RecipeNotes
               WHERE recipe_id=?''', (recipe_id,)
        )
        note_ids = self.c.fetchall()
        ids = []
        for item in note_ids:
            ids.append(self._get_dict_from_row(item)['id'])
        return ids
    
    def update_recipe(self, recipe):
        '''Update a recipe in the database.'''
        recipe_data = [(
            recipe.name,
            recipe.dish_type,
            recipe.author,
            recipe.prep_time,
            recipe.cook_time,
            recipe.source_url,
            recipe.recipe_id
        )]

        self.c.executemany(
            '''UPDATE Recipes
               SET
                name=?,
                dish_type=?,
                author=?,
                prep_time=?,
                cook_time=?,
                source_url=?
               WHERE recipe_id=?''', recipe_data
        )
        
        ingreds = recipe.ingredients
        ingredient_ids = self._get_recipe_ingredients(recipe.recipe_id)
        ingredient_ids = [i['recipe_ingredient_id'] for i in ingredient_ids]
        for idd, item in zip_longest(ingredient_ids, ingreds):
            if not item:
                self.c.execute(
                    '''DELETE FROM RecipeIngredients
                       WHERE recipe_ingredient_id=?''',
                       (idd,)
                )
                continue
            
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
                '''SELECT id
                   FROM IngredientGroups
                   WHERE group_name=?''',
                   (item.group_name,)
            )
            try: 
                group_id = self.c.fetchone()['id']
            except TypeError:
                group_id = None
            
            if idd:
                self.c.execute(
                    '''UPDATE RecipeIngredients
                       SET
                        group_id=?,
                        amount=?,
                        size_id=?,
                        unit_id=?,
                        ingredient_id=?,
                        prep_id=?
                       WHERE recipe_ingredient_id=?''',
                       (group_id,
                        str(item.amount),
                        ingredient_size_id,
                        int(unit_id),
                        int(ingredient_id),
                        prep_id,
                        idd)
                )
            else:
                self.c.execute(
                    '''INSERT into RecipeIngredients(
                        recipe_id,
                        group_id,
                        amount, 
                        size_id, 
                        unit_id, 
                        ingredient_id,
                        prep_id)
                       VALUES(?, ?, ?, ?, ?, ?, ?)''',
                       (recipe.recipe_id,
                        group_id,
                        str(item.amount), 
                        ingredient_size_id,
                        int(unit_id), 
                        int(ingredient_id),
                        prep_id)
                )

        step_ids = self._get_step_ids(recipe.recipe_id)
        for idd, step in zip_longest(step_ids, recipe.steps):
            if step is None:
                self.c.execute(
                    '''DELETE FROM RecipeSteps
                       WHERE id=?''', (idd,)
                )
            
            if idd:
                self.c.execute(
                    '''UPDATE RecipeSteps
                       SET step=?
                       WHERE id=?''',
                       (step, idd)
                )
            else:
                self.c.execute(
                    '''INSERT into RecipeSteps(
                        recipe_id,
                        step)
                       VALUES(?, ?)''',
                       (recipe.recipe_id, step)
                )

        note_ids = self._get_note_ids(recipe.recipe_id)
        for idd, note in zip_longest(note_ids, recipe.notes):
            if note is None:
                self.c.execute(
                    '''DELETE FROM RecipeNotes
                       WHERE id=?''', (idd,)
                )
            
            if idd:
                self.c.execute(
                    '''UPDATE RecipeNotes
                       SET note=?
                       WHERE id=?''',
                       (step, idd)
                )
            else:
                self.c.execute(
                    '''INSERT into RecipeNotes(
                        recipe_id,
                        note)
                       VALUES(?, ?)''',
                       (recipe.recipe_id, note)
                )
        
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
