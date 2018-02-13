import sqlite3
from pyrecipe import DB_FILE

class RecipeDB:
    """A database subclass for pyrecipe"""
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.c = self.conn.cursor()

    def execute(self, command):
        self.c.execute(command)

    def __del__(self):
        self.conn.close()

    def build_db(self):
        self.c.execute('''test''')


if __name__ == '__main__':
    db = RecipeDB()
    db.execute('''hello''')
