"""
	utils for the pyrecipe program

"""
from fractions import Fraction

from .config import *
from .utils import *
from . import ureg, Q_

class Ingredient(object):
	"""The ingredient class is used to build an ingredietns object"""

	def __init__(self, ingredient, amount=None, unit=None, size=None, prep=None, str_format="normal"):
		self.ingredient = ingredient
		self.amount = amount
		self.unit = unit
		self.str_format = str_format
		self.culinary_unit = False
		if self.unit in CULINARY_UNITS:
			self.culinary_unit = True
		self.size = size
		self.prep = prep
	
	
	def __repr__(self):
		return "<Ingredient({}, '{}', '{}', '{}', '{}')>".format(self.amount, 
														   self.size,
														   self.unit, 
														   self.ingredient,
														   self.prep)

	def __str__(self):
		
		if self.str_format == 'shop':
			if self.ingredient == 's&p':
				pass
			elif self.amount == 0 and self.unit == 'taste':
				return "{} to taste".format(self.ingredient.capitalize())
			elif self.prep is None:
				if self.unit == 'each' or self.unit is None:
					return "{} {}".format(self.get_amount(), self.get_ingredient())
				else:
					return "{} {} {}".format(self.get_amount(), self.get_unit(), self.get_ingredient())
			elif self.unit == 'each' or self.unit is None:
				return "{} {}, {}".format(self.get_amount(), self.get_ingredient(), self.prep)
			else:
				return "{} {} {}, {}".format(self.get_amount(), self.get_unit(), self.get_ingredient(), self.prep)
		else:
			if self.ingredient == 's&p':
				return "Salt and pepper to taste"
			elif self.amount == 0 and self.unit == 'taste':
				return "{} to taste".format(self.ingredient.capitalize())
			elif self.prep is None:
				if self.unit == 'each' or self.unit is None:
					return "{} {}".format(self.get_amount(), self.get_ingredient())
				else:
					return "{} {} {}".format(self.get_amount(), self.get_unit(), self.get_ingredient())
			elif self.unit == 'each' or self.unit is None:
				return "{} {}, {}".format(self.get_amount(), self.get_ingredient(), self.prep)
			else:
				return "{} {} {}, {}".format(self.get_amount(), self.get_unit(), self.get_ingredient(), self.prep)
		
			

	def __add__(self, other):
		if self.culinary_unit and other.culinary_unit:
			this_unit = self.amount * ureg[self.unit]
			that_unit = other.amount * ureg[other.unit]
			addition = this_unit + that_unit
			#print(str(addition).split())
			return this_unit + that_unit
		else:
			addition = Fraction(self.amount) + Fraction(other.amount)
			return 2
			#return Ingredient(self.ingredient, addition, self.unit)


		

	def get_ingredient(self):
		if self.amount > 1 and self.unit == 'each':
			return plural(self.ingredient)
		else:
			return self.ingredient

	
	def get_amount(self):
		if self.amount == .3:
			return '1/3'
		elif self.amount == .6:
			return '1/6'
		elif isinstance(self.amount, float) and self.amount < 1:
			return Fraction(self.amount)
		elif isinstance(self.amount, float) and self.amount > 1:
			return improper_to_mixed(str(Fraction(self.amount)))
		else:
			return self.amount

	def get_unit(self):
		if self.unit == 'each':
			pass
		elif int(self.amount) > 1:
			if self.unit in CAN_UNITS:
				return "({})".format(plural(self.unit))
			else:
				return plural(self.unit)
		elif self.amount <= 1:
			if self.unit in CAN_UNITS:
				return "({})".format(self.unit)
			else:
				return self.unit
		else:
			return self.unit

