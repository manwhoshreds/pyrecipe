#!/usr/bin/env python
#from pyrecipe.ingredient import Ingredient

from tkinter import *
import pyrecipe.recipe as recipe

test = recipe.Ingredient("onion", amount=2, unit="tablespoon", prep="chpped")
print(test)
print(test['size'])



#test = IngredientIterator()
#r = recipe.Recipe('pesto')
#print(r)
#print(r['recpe_name'])
#print(r.__dict__)
#print(r.recipe_name)
#print(r.recipe_data)

	
	

