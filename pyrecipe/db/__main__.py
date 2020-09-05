"""
    pyreicpe.db
    ~~~~~~~~~~~
    Dump the database
"""
from pyrecipe.db import dbinfo

recipes = dbinfo.DBInfo().get_recipes()
words = []
for name in recipes:
    #name = name.replace(' ', '_')
    name = name.replace(' ', '\ ')
    words.append(name.lower())

words = ' '.join(words)
print(words)
