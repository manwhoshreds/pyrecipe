"""
    pyreicpe.dbinfo
    ~~~~~~~~~~~~~~~
    
    Info class for retrieving database information
"""
from pyrecipe.db.connection import RecipeDB
from pyrecipe import p

class DBInfo(RecipeDB):
    """Get data from the database as a dict."""
    
    def get_recipes(self):
        """Return all of the recipe names in the database."""
        names = self.c.execute("SELECT name FROM recipes")
        names = [x[0] for x in names]
        return names
    
    def get_recipes_by_dishtype(self, dishtype):
        """Get recipenames of a cirtain dishtype.""" 
        names = self.query(
            "SELECT name FROM recipes WHERE dish_type = \'{}\'".format(dishtype)
        )
        names = [x[0] for x in names]
        return names
    
    def get_recipes_by_author(self, author):
        """Get recipenames of a cirtain dishtype.""" 
        names = self.c.execute(
            "SELECT name FROM recipes WHERE author = \'{}\'".format(author)
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

if __name__ == "__main__":
    test = DBInfo()
    what = test.get_recipes()
    print(len(what))
    #print(test.get_uuid('pesto'))
