from .db import *

DISH_TYPES = [
    'main', 'side', 'dessert', 'condiment', 'dip', 
    'salad dressing', 'sauce', 'base', 'garnish', 'seasoning'
]

def get_data():
    """Get data as dict."""
    db = RecipeDB()
    recipe_data = {}
    
    # recipe names
    recipe_names = db.query('SELECT name FROM Recipes')
    recipe_names = [x[0] for x in recipe_names]
    recipe_data['recipe_names'] = recipe_names

    # dish type names, look how elegant and compact. :)
    for item in DISH_TYPES:
        names = db.query(
            "SELECT name FROM Recipes WHERE dish_type = \'{}\'".format(item)
        )
        names = [x[0] for x in names]
        dict_key = '{}_names'.format(item.replace(' ', '_'))
        recipe_data[dict_key] = names

    # recipe uuid's
    uuids = db.query(
        'SELECT name, recipe_uuid FROM Recipes'
    )
    recipe_data['uuids'] = {}
    for item in uuids:
        recipe_data['uuids'][item[0]] = item[1]
    

    return recipe_data


