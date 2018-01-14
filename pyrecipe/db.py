import sqlite3
from pyrecipe import DB_FILE

class RecipeDB:
    """A database subclass for pyrecipe"""
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.c = self.conn.curser()

    def exucute(self):
        pass


