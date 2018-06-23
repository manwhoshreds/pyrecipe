from pyrecipe.db import RecipeDB

class DBInfo(RecipeDB):
    """Get data from the database as a dict."""
    
    def get_recipe_names(self):
        """Return all of the recipe names in the database."""
        names = self.query("SELECT name FROM recipes")
        names = [x[0] for x in names]
        return names
    
    def get_dishtype(self, dishtype):
        """Get recipenames of a cirtain dishtype.""" 
        names = self.query(
            "SELECT name FROM recipes WHERE dish_type = \'{}\'".format(dishtype)
        )
        names = [x[0] for x in names]
        return names
    
    def get_uuid(self, name):
        """Get the uuid of the recipe."""
        uuid = self.query(
            "SELECT recipe_uuid FROM recipes WHERE name = \'{}\' COLLATE NOCASE".format(name)
        )[0][0]
        return uuid


if __name__ == "__main__":
    test = DBInfo()
    print(len(test.get_recipe_names()))
    print(test.get_uuid('pesto'))
