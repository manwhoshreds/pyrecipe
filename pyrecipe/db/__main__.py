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

test = get_data()['recipe_names']
words = []
for item in test:
    i = item.replace(' ', '\ ')
    words.append(i)

words = ' '.join(words)
print(words)
