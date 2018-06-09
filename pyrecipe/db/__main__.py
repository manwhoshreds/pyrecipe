"""
    pyreicpe.db
    ~~~~~~~~~~~
    Dump the database
"""
from pyrecipe.db import get_data
import pprint


#PP = pprint.PrettyPrinter()
#test = get_data()
#PP.pprint(test)

names = get_data()['recipe_names']
words = []
for name in names:
    name = name.replace(' ', '_')
    words.append(name.lower())

words = ' '.join(words)
print(words)
