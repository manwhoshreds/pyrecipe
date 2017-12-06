#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
	pyrecipe.recipe
	~~~~~~~~~~~~~~~
	The recipe module contains the main recipe
	classes used to interact with ORD (open recipe document) files. 
	You can simply print the recipe or print the xml dump.
"""

import os
import sys
import yaml
import random
import sys
import subprocess
import sqlite3
import datetime
# dubug
import pdb

from fractions import Fraction
from lxml import etree
from pint.errors import *
from . import ureg, Q_

from .utils import *
from .config import *
from .config import __version__, __scriptname__, __email__
from .ingredient import *

color = Color()

class Recipe:
	"""
		The recipe class is used to perform operations on
		recipe source files such as print and save xml.
	"""
	
	def __init__(self, source, checkfile=True):
		# TODO bad yaml breaks autocompletion for some reason
		self.source = get_file_name(source)
		if self.source in RECIPE_FILES:
			pass
		else:
			self.source = source
			if not self.source.endswith(".recipe"):
				sys.exit("{}ERROR: {} is not a recipe file. Exiting..."
				         .format(color.ERROR, self.source))

		
		with open(self.source, "r") as stream:
			try:
				self.recipe_data = yaml.safe_load(stream)
			except yaml.YAMLError as exc:
				print(exc)
				sys.exit(1)
		
		# cache the xml data
		self.xml_data = ''

		# complete string representation of the recipe
		self.recipe_string = ''
		
		# scan the recipe to cache all data
		self._scan_recipe()
		
		# check file for syntax error before we can continue
		self.check_file(silent=True)
	
	def __str__(self):
		"""
			returns the complete string representation
			of the recipe data

		"""
		return self.recipe_string

	def _scan_recipe(self):
		"""used to extract all the values out of a recipe
		source file while building xml at the same time

		"""
		self.root = etree.Element("recipe")
		self.mainkeys = self.recipe_data.keys()
		
		# recipe name	
		if 'recipe_name' in self.mainkeys:
			self.recipe_name = self.recipe_data['recipe_name'] 
			xml_recipe_name = etree.SubElement(self.root, "name")
			xml_recipe_name.text = self.recipe_name

		# recipe_uuid
		if 'recipe_uuid' in self.mainkeys:
			self.recipe_uuid = self.recipe_data['recipe_uuid']
			xml_recipe_uuid = etree.SubElement(self.root, "uuid")
			xml_recipe_uuid.text = self.recipe_uuid

		# category
		if 'category' in self.mainkeys:
			self.category = self.recipe_data['category']
			for entry in self.category:
				xml_category = etree.SubElement(self.root, "category")
				xml_category.text = str(entry)
		
		# author
		if 'author' in self.mainkeys:
			self.author = self.recipe_data['author']
			xml_author = etree.SubElement(self.root, "author")
			xml_author.text = self.author

		# prep_time
		if 'prep_time' in self.mainkeys:
			self.prep_time = self.recipe_data['prep_time']
			xml_prep_time = etree.SubElement(self.root, "prep_time")
			xml_prep_time.text = str(self.prep_time)

		# cook_time
		if 'cook_time' in self.mainkeys:
			self.cook_time = self.recipe_data['cook_time']
			xml_cook_time = etree.SubElement(self.root, "cook_time")
			xml_cook_time.text = str(self.cook_time)

		# bake_time
		if 'bake_time' in self.mainkeys:
			self.bake_time = self.recipe_data['bake_time']
			xml_bake_time = etree.SubElement(self.root, "bake_time")
			xml_bake_time.text = str(self.bake_time)

		# notes
		if 'notes' in self.mainkeys:
			self.notes = self.recipe_data['notes']

		# price
		if 'price' in self.mainkeys:
			self.price = self.recipe_data['price']
			xml_price = etree.SubElement(self.root, "price")
			xml_price.text = str(self.price)
		
		# oven_temp
		if 'oven_temp' in self.mainkeys:
			self.oven_temp = self.recipe_data['oven_temp']
			self.ot_amount = self.recipe_data['oven_temp']['amount']
			self.ot_unit = self.recipe_data['oven_temp']['unit']
			xml_oven_temp = etree.SubElement(self.root, "oven_temp")
			xml_oven_temp.text = str(self.ot_amount) + " " + str(self.ot_unit)
		
		# dish_type
		if 'dish_type' in self.mainkeys:
			self.dish_type = self.recipe_data['dish_type']
			xml_dish_type = etree.SubElement(self.root, "dish_type")
			xml_dish_type.text = self.dish_type

		# yields
		if 'yields' in self.mainkeys:
			self.yields = self.recipe_data['yields']
			xml_yields = etree.SubElement(self.root, "yields")
			for yeld in self.yields:
				xml_servings = etree.SubElement(xml_yields, "servings")
				xml_servings.text = str(yeld)

		if 'ingredients' in self.mainkeys:
			self.ingredient_data = self.recipe_data['ingredients']
		
		# alt_ingredients
		if 'alt_ingredients' in self.mainkeys:
			self.alt_ingredient_data = self.recipe_data['alt_ingredients']
			self.alt_ingredients = []
			# building a list of alternative ingredient names here helps later
			# in get_ingredients()
			for item in self.alt_ingredient_data.keys():
				self.alt_ingredients.append(item)
		
		# steps	
		if 'steps' in self.mainkeys:
			self.steps = self.recipe_data['steps']
		
		self._process_xml()
	
	def check_file(self, silent=False):
			"""function to validate Open Recipe Format files"""
			
			failure_keys = []
			failure_units = []
			failure_prep_types = []
			# amounts must be numbers
			failure_amounts = []
			failed = False
			
			for item in self.ingredient_data:
				try:	
					amount = item['amounts'][0].get('amount', None)
					if isinstance(amount, int) or isinstance(amount, float):
						pass
					else:
						failure_amounts.append(item['name'])
						failed = True
				except KeyError:
					continue
			
			for item in REQUIRED_ORD_KEYS:
				if item not in self.mainkeys:
					failure_keys.append(item)
					failed = True
			
			for item in self.ingredient_data:
				try:
					unit = item['amounts'][0]['unit']
					if unit not in ALLOWED_INGRED_UNITS:
						failure_units.append(unit)
						failed = True
				except KeyError:
					continue
			
			for item in self.ingredient_data:
				try:
					prep = item['prep']
					if prep not in PREP_TYPES and prep not in failure_prep_types:
						failure_prep_types.append(prep)
						failed = True
				except KeyError:
					continue
			
			if failed:
				if silent:
					return True
				else:
					if len(failure_keys) > 0:
						print(color.ERROR 
							+ self.source
							+ ": The following keys are required by the ORD spec: " 
							+ ",".join(failure_keys) 
							+ color.NORMAL)
					
					if len(failure_units) > 0:
						print(color.ERROR 
							+ self.source
							+ ": The following units are not allowed by the ORD spec: " 
							+ ", ".join(failure_units)
							+ color.NORMAL)
					
					if len(failure_amounts) > 0:
						print(color.ERROR 
							+ self.source
							+ ": The following ingredients have no integer amounts: " 
							+ ", ".join(failure_amounts) 
							+ color.NORMAL)
					
					if len (failure_prep_types) > 0:
						print(color.ERROR 
							+ self.source
							+ ": The following prep types are not allowed by the ORD spec: " 
							+ ", ".join(failure_prep_types) 
							+ color.NORMAL)
					
					if self.recipe_data['dish_type'] not in DISH_TYPES:
						print(color.ERROR 
							+ self.source
							+ ": The current dish type is not in the ORD spec: " 
							+ self.recipe_data['dish_type'] 
							+ color.NORMAL)
					
					if len(self.steps) < 1:
						print(color.ERROR 
							+ self.source
							+ ": You must at least supply one step in the recipe." 
							+ color.NORMAL)
			else:	
				if silent:
					return False
				else:
					print(color.TITLE 
						+ self.source
						+ " is a valid ORD file")
	
	def get_ingredients(self, amount_level=0, alt_ingred=None):	
		"""Returns a list of ingredients."""

		ingredients = []
		if alt_ingred:	
			ingredient_data = self.alt_ingredient_data[alt_ingred]
		else:
			ingredient_data = self.ingredient_data
		
		for item in ingredient_data:
			name = item['name']
			if name == 's&p':
				ingred = Ingredient('s&p')
				ingredients.append(str(ingred))
				continue
			amount = item['amounts'][amount_level].get('amount', 0)
			unit = item['amounts'][amount_level].get('unit', None)
			size = item.get('size', None)
			prep = item.get('prep', None)
			ingred = Ingredient(name, unit=unit, amount=amount, size=size, prep=prep)
			ingredients.append(str(ingred))
		
		return ingredients
	
	
	def print_recipe(self, verb_level=0):
		"""Print recipe to standard output."""
	
		print("\n"
			+ color.RECIPENAME 
		    + self.recipe_name 
			+ color.NORMAL
			+ "\n")
		
		if verb_level >= 1:
			try:
				print("Prep time: {} min.".format(str(self.prep_time)))
			except AttributeError:
				pass
			try:
				print("Cook time: {} min.".format(str(self.cook_time)))
			except AttributeError:
				pass
			try:
				print("Bake time: {} min.".format(str(self.bake_time)))
			except AttributeError:
				pass
			try:
				print("Oven temp: {} {}".format(str(self.oven_temp['amount']), self.oven_temp['unit']))
			except AttributeError:
				pass
			try:
				print("Price: {}".format(self.price))
			except AttributeError:
				pass
				
		if verb_level >= 2:
			try:
				print("Author: {}".format(self.author))
			except AttributeError:
				pass
			try:
				print("URL: {}".format(self.url))
			except AttributeError:
				pass
			try:
				print("Category(s): " + ", ".join(self.category))
				
			except AttributeError:
				pass
			try:
				print("Yields: " + str(self.YIELDS))
			except AttributeError:
				pass
			try:
				if self.NOTES:
					print(S_DIV)
					print("NOTES:")
					for note in self.NOTES:
						print(note)
			except AttributeError:
				pass


		print(S_DIV + color.TITLE + "\nIngredients:" + color.NORMAL)
		# Put together all the ingredients
		for ingred in self.get_ingredients():	
			print(ingred)
		try:	
			for item in self.alt_ingredients:
				print("\n{}{}{}".format(color.TITLE, item.title(), color.NORMAL))
				
				for ingred in self.get_ingredients(alt_ingred=item):
					print(ingred)
		except AttributeError:
			pass
		
		print("\n"
			+ S_DIV
			+ color.TITLE
			+ "\nMethod:"
			+ color.NORMAL
		)	
		
		# print steps	
		for index, step in enumerate(self.steps, start=1):
			print("{}{}.{} {}".format(color.NUMBER, index, color.NORMAL, step['step']))
	
	
	def _process_xml(self):
		"""
			process recipe data into xml

		"""
		# normal ingredients (i.e. not alternative ingredients as can be found below)
		xml_ingredients = etree.SubElement(self.root, "ingredients")
		for ingred in self.get_ingredients(): 	
			xml_ingred = etree.SubElement(xml_ingredients, "ingred")
			xml_ingred.text = ingred
		
		try:	
			for item in self.alt_ingredients:
				xml_alt_ingredients = etree.SubElement(self.root, "alt_ingredients")
				xml_alt_ingredients.set('alt_name', item.title())
				
				for ingred in self.get_ingredients(alt_ingred=item):
					xml_alt_ingred = etree.SubElement(xml_alt_ingredients, "alt_ingred")
					xml_alt_ingred.text = ingred
		except AttributeError:
			pass
		
		steps = etree.SubElement(self.root, "steps")

		for step in self.steps:
			steps_of = etree.SubElement(steps, "step")
			steps_of.text = step['step']
			
		result = etree.tostring(self.root,
							xml_declaration=True,
							encoding='utf-8',
							with_tail=False,
							method='xml',
							pretty_print=True)
		
		self.xml_data += result.decode('utf-8')


class ShoppingList:
	# TODO Lots of work to do in the ShoppingList cls in general
	"""Class to create and display a shopping list"""
	shopping_dict = {}
	recipe_names = []
	dressing_names = []
	def _proc_ingreds(self, file_name, alt_ingred=""):
		#TODO-> Serious flaw in this logic, work on it
		sd = ShoppingList.shopping_dict
		r = Recipe(file_name)
		if alt_ingred:
			ingreds = r.alt_ingredient_data[alt_ingred]
		else:
			ingreds = r.ingredient_data
		for item in ingreds:
			name = item['name']
			try:
				link = item['link']
				self.update(link)
			except KeyError:
				pass
				
			if name == "s&p":
				continue
			amount = item['amounts'][0].get('amount', 0)
			unit = item['amounts'][0].get('unit', None)
			ingred = Ingredient(name, amount=amount, unit=unit)
			# check if name already in sd so we can add together
			if name	in sd.keys():
				orig_amount = sd[name][0]
				orig_unit   = sd[name][1]	
				orig_ingred = Ingredient(name, amount=orig_amount, unit=orig_unit)
				addition = ingred + orig_ingred
				sd[name] = str(addition).split()
			else:
				sd[name] = [ingred.get_amount(), ingred.get_unit()]
				
	def write_to_xml(self):
		"""Write the shopping list to an xml file after
		   building.
		"""
		date = datetime.date
		today = date.today()
		root = etree.Element("shopping_list")	
		sd = ShoppingList.shopping_dict
		
		date = etree.SubElement(root, "date")
		date.text = str(today)
		xml_maindish_names = etree.SubElement(root, "main_dishes")
		xml_salad_dressing = etree.SubElement(root, "salad_dressing")
		xml_ingredients = etree.SubElement(root, "ingredients")
		
		# Add recipe names to the tree
		for item in ShoppingList.recipe_names:
			xml_main_dish = etree.SubElement(xml_maindish_names, "name")
			xml_main_dish.text = str(item)
		
		# the salad dressing names
		for item in ShoppingList.dressing_names:
			xml_dressing_name = etree.SubElement(xml_salad_dressing, "name")
			xml_dressing_name.text = str(item)

		# finally, ingreds
		for key, value in sd.items():
			ingred = "{} {} {}".format(key, str(value[0]), str(value[1]))
			xml_shopping_list_item = etree.SubElement(xml_ingredients, "ingredient")
			xml_shopping_list_item.text = str(ingred)
			
		
		result = etree.tostring(root,
								xml_declaration=True,
								encoding='utf-8',
								with_tail=False,
								method='xml',
								pretty_print=True)
		
		#print("\n{}Writing shopping list to {}{}".format(color.INFORM, SHOPPING_LIST_FILE, color.NORMAL))
		#with open(SHOPPING_LIST_FILE, "w") as f:
		#	f.write(result.decode("utf-8"))
	
	def return_list(self):
		return ShoppingList.shopping_dict

	def update(self, source):
		"""Return a shopping list of ingredients from a 
		   list of recipes. If duplicate entries are found,
		   ingredients are added together.
		"""
		r = Recipe(source)
		if r.dish_type == "salad dressing":
			ShoppingList.dressing_names.append(r.recipe_name)
		else:
			ShoppingList.recipe_names.append(r.recipe_name)
		
		self._proc_ingreds(source)
		try:
			alt_ingreds = r.alt_ingredients
			for item in alt_ingreds:
				self._proc_ingreds(source, alt_ingred=item)
		except AttributeError:
			pass

	def	print_list(self):
		mdn = ShoppingList.recipe_names
		sd = ShoppingList.shopping_dict
		dn = ShoppingList.dressing_names
		
		print("Recipes:\n")
		for item in mdn:
			print(item)
		print("\n" + S_DIV)

		if len(dn) > 0:
			print("Salad Dressings:\n")
			for item in dn:
				print(item)
			print("\n{}".format(S_DIV))

		# Print list	
		PP.pprint(sd)
		for key, value in sd.items():
			print("{}, {} {}".format(key, value[0], value[1]))
		# write the list to an xml file	
		self.write_to_xml()
	
	def random_recipes(self, random_count=RAND_RECIPE_COUNT):
		"""Return random recipes and build a shopping list of ingredients needed"""	
		#TODO-> Use the shopping list class to make this shopping list too.

		sl = ShoppingList()
		try:
			recipe_sample = random.sample(MAINDISH_NAMES, random_count)
			salad_dressing_random = random.choice(DRESSING_NAMES)
		except ValueError:
			sys.exit("{}ERROR: Random count is higher than "
				     "the amount of recipes available ({}). "
				     "Please enter a lower number."
				     .format(color.ERROR, str(len(MAINDISH_NAMES))))
		
		sl.update(salad_dressing_random)
		for dish in recipe_sample:
			sl.update(dish)
		
		self.print_list()


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


class DataBase:
	
	def __init__(self, db_file):
		self.db_file =	db_file

	def connect(self):
		conn = sqlite3.connect(db_file)
		c = conn.cursor()


###########
# functions
def template(recipe_name):
	"""Start the interactive template builder"""
	
	try:
		print("Interactive Template Builder. Press Ctrl-c to abort.\n")
		template = ""
		template += "recipe_name: {}\n".format(recipe_name)
		# check if file exist, lets catch this early so we can exit before entering in all the info
		file_name = get_file_name(recipe_name)
		if os.path.isfile(file_name):
			print("File with this name already exist in directory exiting...")
			exit(1)
		while True:
			dish_type = input("Enter dish type: ")
			if dish_type not in DISH_TYPES:
				print("Dish type must be one of {}".format(", ".join(DISH_TYPES)))
				continue
			else:
				break
		template += "dish_type: {}\n".format(dish_type)
		prep_time = input("Enter prep time: ")
		template += "prep_time: {}\n".format(prep_time)
		cook_time = input("Enter cook time (optional): ")
		if cook_time:
			template += "cook_time: {}\n".format(cook_time)
		author = input("Enter authors full name: ")
		template += "author: {}\n".format(author)
		ingred_amount = 0
		while True:
			try:
				ingred_amount = int(input("Enter amount of ingredients: "))
			except ValueError:
				print("Input must be a number")
				continue
			else:
				break
		template += "ingredients:\n"
		for item in range(ingred_amount):
			template += "    - name:\n      amounts:\n        - amount:\n          unit:\n"
		template += "steps:\n  - step: Coming soon"
		template += "\n# vim: set expandtab ts=4 syntax=yaml:"
		print("Writing to file... " + file_name)
		with open(file_name, "w") as tmp:
			tmp.write(str(template))
	
	except KeyboardInterrupt:
		print("\nExiting...")
		sys.exit(0)
	
	subprocess.call([EDITOR, file_name])

def version():
	"""Print the current version of pyrecipe and exit."""

	print("{}                _              _              _ {}  {} v{}".format(color.INFORM, color.NORMAL, __scriptname__, __version__))
	print("{}               (_)            | |            | |{}  The recipe management program.".format(color.INFORM, color.NORMAL))
	print("{}  _ __ ___  ___ _ _ __   ___  | |_ ___   ___ | |{}".format(color.INFORM, color.NORMAL))
	print("{} | '__/ _ \/ __| | '_ \ / _ \ | __/ _ \ / _ \| |{}  For any questions, contact me at {}".format(color.INFORM, color.NORMAL, __email__))
	print("{} | | |  __/ (__| | |_) |  __/ | || (_) | (_) | |{}  or type recipe_tool --help for more info.".format(color.INFORM, color.NORMAL))
	print("{} |_|  \___|\___|_| .__/ \___|  \__\___/ \___/|_|{}".format(color.INFORM, color.NORMAL))
	print("{}                 | |                            {}  This program may be freely redistributed under".format(color.INFORM, color.NORMAL))
	print("{}                 |_|                            {}  the terms of the GNU General Public License.".format(color.INFORM, color.NORMAL))

def stats(verb=0):
	"""Print statistics about your recipe database and exit."""
	
	version()
	print("Recipes: {}".format(len(RECIPE_FILES)))
	if verb >= 1:
		print("Recipe directory: {}".format(RECIPE_DATA_DIR))
		print("Recipe xml directory: {}".format(RECIPE_XML_DIR))
		print("Default random recipe: {}".format(RAND_RECIPE_COUNT))



