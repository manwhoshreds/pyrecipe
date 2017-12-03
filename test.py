#!/usr/bin/env python 
from pyrecipe.recipe import *
import pdb

test = Ingredient("onion", 3, "teaspoon")
test2 = Ingredient("onion", 3, "tablespoon", prep="diced", shop=True)
print(str(test2))

pdb.set_trace()
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



