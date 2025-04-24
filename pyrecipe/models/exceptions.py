# pyrecipe/models/database.py


class RecipeNotFound(Exception):
    """Raised when someone asks for a recipe name or ID that does not exist."""
    pass

