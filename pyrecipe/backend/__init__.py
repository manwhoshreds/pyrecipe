from .database import RecipeDB, DB_FILE, RecipeNotFound, DBInfo
from .webscraper import SCRAPEABLE_SITES
from .recipe import Recipe

SIZE_STRINGS = ['large', 'medium', 'small', 'heaping']
DISH_TYPES = [
    'main', 'side', 'dessert', 'condiment', 'dip', 'prep',
    'salad dressing', 'sauce', 'base', 'garnish', 'seasoning'
]

