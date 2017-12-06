"""
	utils for the pyrecipe program

"""
from fractions import Fraction

from .config import *
from .utils import *
from . import ureg, Q_

class Ingredient(object):
	"""The ingredient class is used to build an ingredietns object"""

	def __init__(self, ingredient, amount='', size='', unit='', prep='', str_format="normal"):
		self._ingredient = ingredient
		self._amount = amount
		self._size = size
		self._unit = unit
		self._prep = prep
		self.culinary_unit = False
		if self._unit in CULINARY_UNITS:
			self.culinary_unit = True
		self.str_format = str_format
		self._after_init()
	
	def __repr__(self):
		return "<Ingredient({}, '{}', '{}', '{}', '{}')>".format(self.amount, 
														   self.size,
														   self.unit, 
														   self.ingredient,
														   self.prep)

	def _after_init(self):
		self.amount = self.get_amount()
		self.size = self._size
		self.unit = self.get_unit()
		self.ingredient = self.get_ingredient()

	def __str__(self):
		# TODO try changing this to a one or two liner
		
		if self.str_format == "shop":
			self._shop_str_formater()

		else:
			if self.ingredient == 's&p':
				return "Salt and pepper to taste"
			elif self.amount == 0 and self.unit == 'taste':
				return "{} to taste".format(self.ingredient.capitalize())
			elif self._prep is None:
				if self.unit == 'each' or self.unit is None:
					return "{} {}".format(self.get_amount(), self.get_ingredient())
				else:
					return "{} {} {}".format(self.get_amount(), self.get_unit(), self.get_ingredient())
			elif self.unit == 'each' or self.unit is None:
				return "{} {}, {}".format(self.get_amount(), self.get_ingredient(), self._prep)
			else:
				return "{} {} {}, {}".format(self.get_amount(), self.get_unit(), self.get_ingredient(), self._prep)
		
	def _shop_str_formater(self):
		if self.ingredient == 's&p':
			pass
		elif self.amount == 0 and self.unit == 'taste':
			pass
		elif self.unit == 'each' or self.unit is None:
			return "{} {}, {}".format(self.get_amount(), self.get_ingredient(), self._prep)
		else:
			return "{} {} {}, {}".format(self.get_amount(), self.get_unit(), self.get_ingredient(), self._prep)

	def __add__(self, other):
		if self.culinary_unit and other.culinary_unit:
			this_unit = self.amount * ureg[self.unit]
			that_unit = other.amount * ureg[other.unit]
			addition = this_unit + that_unit
			#print(str(addition).split())
			return this_unit + that_unit
		else:
			addition = self.amount + other.amount
			return Ingredient(self.ingredient, addition, self.unit)


		

	def get_ingredient(self):
		if self._amount > 1 and self._unit == 'each':
			return plural(self._ingredient)
		else:
			return self._ingredient

	
	def get_amount(self):
		if self._amount == .3:
			return '1/3'
		elif self._amount == .6:
			return '1/6'
		elif isinstance(self._amount, float) and self._amount < 1:
			return Fraction(self._amount)
		elif isinstance(self._amount, float) and self._amount > 1:
			return improper_to_mixed(str(Fraction(self._amount)))
		else:
			return self._amount

	def get_unit(self):
		if self._unit == 'each':
			return ''
		elif int(self._amount) > 1:
			if self._unit in CAN_UNITS:
				return "({})".format(plural(self.unit))
			else:
				return plural(self._unit)
		elif self._amount <= 1:
			if self._unit in CAN_UNITS:
				return "({})".format(self._unit)
			else:
				return self._unit
		else:
			return self._unit

