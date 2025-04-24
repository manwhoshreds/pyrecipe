from models import PyRecipe

class Controller:
    """Controller for pyrecipe"""
    
    def _analyze_source(self, source):
        if re.compile(r'^https?\://').search(source):
            return 'is_url'
        else:
            with RecipeDB() as db:
                if source in db.get_all_recipes():
                    return 'is_in_db'
                else:
                    return 'new_recipe'
    
 ;   def _scrape_recipe(self, source):
        rec = Recipe()
        scraper = RecipeWebScraper()
        rec = scraper.scrape(source, rec)
        return rec
    
    def _load_from_database(self, source):
        with RecipeDB() as db:
            rec = db.read_recipe(source)
        return rec

    def read_recipe(self, source):
        a_source = self._analyze_source(source) 
        handler = {
                'is_url': self._scrape_recipe,
                'is_in_db': self._load_from_database,
                'new_recipe': self.recipe
        }
        return handler[a_source](source)

    def create_recipe(self, recipe: Recipe):
        with RecipeDB() as db:
            db.create_recipe(recipe)

    def delete_recipe(self, recipe_name):
        with RecipeDB() as db:
            if db.recipe_exists(recipe_name):
                db.delete_recipe(recipe_name)
            else:
                raise RecipeNotFound()

    def update_recipe(self, recipe: Recipe):
        with RecipeDB() as db:
            db.update_recipe(recipe)

    
    def get_all_recipes(self):
        with RecipeDB() as db:
            recs = db.get_all_recipes()
        return recs

    def recipe(self, source):
        return Recipe(name=source)
