from .dbinfo import DBInfo
from .connection import RecipeDB as DBConn
from .connection import (delete_recipe, update_db)

dbinfo = DBInfo()

DISH_TYPES = [
    'main', 'side', 'dessert', 'condiment', 'dip', 'prep',
    'salad dressing', 'sauce', 'base', 'garnish', 'seasoning'
]

