#!/usr/bin/env python
#from pyrecipe.ingredient import Ingredient
import re
from pint import UnitRegistry

ureg = UnitRegistry()
ok = ureg.__dict__
#ingred = Ingredient(ingredient='mushroom',
#					amount=1, 
					#size='large', 
#					unit='tablespoon',
#					prep='diced')
#ingred = ingred.__dict__
#class Default(dict):
#	def __missing__(self, key):
#		return '{'+key+'}'

#test = "{} {} {} {} {}".format(ingred['amount'], ingred['size'], ingred['unit'], 
#						   ingred['ingredient'], ingred['_prep'])
#test1 = "{amount} {size} {unit} {ingredient} {_prep}".format_map(Default(ingred))


#def test():
#	string  = "helllo"
#	return string

#print(test())
#this = re.sub(' +', ' ', test)

#print(str(ingred))

def gen():
	for i in range(10):
		yield i

for i in gen():	
	print(i)
	


