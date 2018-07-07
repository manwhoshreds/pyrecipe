from pyrecipe.recipe import Recipe
from pyrecipe.config import RECIPE_DATA_FILES

for fi in RECIPE_DATA_FILES:
    r = Recipe(fi)
    if r.name == "Garam Masala":
        print(r.name)
        print(r.uuid)
        print(r.file_name)
        print(fi)
