#!/usr/bin/env python
from pyrecipe.ingredient import Ingredient
import re
from pint import UnitRegistry

ureg = UnitRegistry()
ok = ureg.__dict__
print(ok)
print(self._amount)
ingred = Ingredient(ingredient='mushroom',
					amount=1, 
					#size='large', 
					unit='tablespoon',
					prep='diced')
ingred = ingred.__dict__
print(ingred)
print(dir(ingred))
class Default(dict):
	def __missing__(self, key):
		return '{'+key+'}'

test = "{} {} {} {} {}".format(ingred['amount'], ingred['size'], ingred['unit'], 
						   ingred['ingredient'], ingred['_prep'])
test1 = "{amount} {size} {unit} {ingredient} {_prep}".format_map(Default(ingred))
#this = re.sub(' +', ' ', test)
print(test1)

#print(str(ingred))


