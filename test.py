#!/usr/bin/env python 
from pyrecipe.recipe import *

test = Ingredient(1.5, "each", "onion")
print(repr(test))
print(str(test))

def columnify(iterable):
    # First convert everything to its repr
    strings = [repr(x) for x in iterable]
    # Now pad all the strings to match the widest
    widest = max(len(x) for x in strings)
    padded = [x.ljust(widest) for x in strings]
    return padded
def colprint(iterable, width=72):
    columns = columnify(iterable)
    colwidth = len(columns[0])+2
    perline = (width-4) // colwidth
    print('[ ', end='')
    for i, column in enumerate(columns):
        print(column, end=', ')
        if i % perline == perline-1:
            print('\n  ', end='')
    print(' ]')



