from .dbinfo import DBInfo
from .connection import RecipeDB as DBConn, DB_FILE
from .connection import (delete_recipe, update_db)


DISH_TYPES = [
    'main', 'side', 'dessert', 'condiment', 'dip', 'prep',
    'salad dressing', 'sauce', 'base', 'garnish', 'seasoning'
]

