#!/usr/bin/env python
# -*- encoding: UTF-8 -*-
"""
	pyrecipe.recipe
	~~~~~~~~~~~~~~~
	The recipe module lets contains the main recipe
	classes used to interact with ORD (open recipe document) files. 
	You can simply print the recipe or print the xml dump.
"""

import os
import sys
import yaml
import pprint
import random
import sys
import subprocess
import sqlite3
import datetime

from fractions import Fraction
from lxml import etree
from pint.errors import *
from . import ureg, Q_

from .config import *
from .config import __version__, __scriptname__, __email__




# helpers
def _plural(word):
	es_plurals = ['tomato',
				  'roma tomato',
				  'potato']
	
	if word in es_plurals:
		return word + 'es'
	else:
		return word + 's'


def _md5():
	#TODO-> md5 funtion to check which yaml files have changed and then write the coresponding xml.
	pass


def _improper_to_mixed(fraction):
	str_frac = str(fraction)
	x = str_frac.split('/')
	num = int(x[0])
	den = int(x[1])
	whole_part = num // den
	fract_part = num % den
	return "{} {}/{}".format(whole_part, fract_part, den)


class Color:
	"""
	   The color class defines various colors for 
	   use in pyrecipe output.
	"""
	
	NORMAL = '\033[m'
	ERROR = '\033[1;31m'
	RECIPENAME = '\033[1;36m'
	TITLE = '\033[36m'
	NUMBER = '\033[1;33m'
	REGULAR = '\033[1;35m'
	LINE = '\033[1;37m'
	INFORM = '\033[1;36m'

color = Color()


class Recipe:
	"""
		The recipe class is used to perform operations on
		recipe source files such as print and save xml.
	"""
	
	def __init__(self, source):
		
		# i need color
		self.source = source
		db = DataBase(DB_FILE)
		
		if not source.endswith(".recipe"):
			print("{}ERROR: {} is not a recipe file. Exiting...".format(color.ERROR, source))
			sys.exit(1)
		else:
			with open(source, "r") as stream:
				try:
					self.recipe_data = yaml.safe_load(stream)
				except yaml.YAMLError as exc:
					print(exc)
					sys.exit(1)

		self.root = etree.Element("recipe")
		self.mainkeys = self.recipe_data.keys()

		"""__init__: extract all variables from recipe source file
		and put it in to class variables. We also start building
		xml here.
		"""	
		#TODO-> make these vairables better
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
			yields = self.recipe_data['yields']
			xml_yields = etree.SubElement(self.root, "yields")
			for yeld in yields:
				xml_servings = etree.SubElement(xml_yields, "servings")
				xml_servings.text = str(yeld)

		# more complex and nested. Also, these do not update the xml tree,
		# this is done later on in program
		# ingredients
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
		
		if not self.check_file(silent=True): 
			exit(0)

	def __str__(self):
		return "Im testing the function of the __str__ method"


	def check_file(self, silent=False):
		"""function to validate Open Recipe Format files"""
		
		failure_keys = []
		failure_units = []
		failure_prep_types = []
		# amounts must be numbers
		failure_amounts = []
		failure_point = 0
		
		for item in self.ingredient_data:
			try:	
				amount = item['amounts'][0]['amount']
				if isinstance(amount, int) or isinstance(amount, float):
					pass
				else:
					failure_amounts.append(item['name'])
					failure_point += 1
			except KeyError:
				continue
		
		for item in REQUIRED_ORD_KEYS:
			if item not in self.mainkeys:
				failure_keys.append(item)
				failure_point += 1
		
		for item in self.ingredient_data:
			try:
				unit = item['amounts'][0]['unit']
				if unit not in ALLOWED_INGRED_UNITS:
					failure_units.append(unit)
					failure_point += 1
			except KeyError:
				continue
		
		for item in self.ingredient_data:
			try:
				prep = item['prep']
				if prep not in PREP_TYPES and prep not in failure_prep_types:
					failure_prep_types.append(prep)
					failure_point += 1
			except KeyError:
				continue
		
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
		
		if failure_point == 0:
			if silent == False:
				print(color.TITLE 
					+ self.source 
					+ " is a valid ORD file")
			else:
				return True
		else:
			return False
	
			
	def get_ingredients(self, amount_level=0, alt_ingred=None):	
		"""Returns a list of ingredients."""

		ingredients = []
		if alt_ingred:	
			ingredient_data = self.alt_ingredient_data[alt_ingred]
		else:
			ingredient_data = self.ingredient_data
		
		for item in ingredient_data:
			ingred_string = ""
			name = item['name']
			if name == "s&p":
				ingred_string += "salt and pepper to taste"
				ingredients.append(ingred_string)
				continue
			amount = item['amounts'][amount_level].get('amount', 0)
			try:	
				size = item['size']
			except KeyError:
				pass
			try:
				prep = item['prep']
			except KeyError:
				pass
			unit = item['amounts'][amount_level]['unit']
			if unit == "taste":
				ingred_string += "{} to taste".format(name.capitalize())
				ingredients.append(ingred_string)
				continue
			if unit in CAN_UNITS:
				unit = "({})".format(unit)
			if amount < 1:
				if amount == .333:
					ingred_string += "1/3"
				else:
					ingred_string += str(Fraction(amount))
			elif type(amount) is float:
				ingred_string += _improper_to_mixed(str(Fraction(amount)))
			else:
				ingred_string += str(amount)
			if 'size' in locals():
				ingred_string += " " + size
				del size
			if unit == "pinch":
				ingred_string += "pinch of {}".format(name)
				ingredients.append(ingred_string)
				continue
			if unit == "each":
				if amount > 1:
						ingred_string += " " + _plural(name)
				else:
					ingred_string += " " + name
				ingredients.append(ingred_string)
				continue
			if amount > 1:
				ingred_string += " " + _plural(unit)
			else:
				ingred_string += " " + unit

			ingred_string += " " + name
			# prep, as in chopped, diced, etc.., 
			# indicated after the ingred string following a comma
			try:
				ingred_string += ", {}".format(prep)
				del prep
			except UnboundLocalError:
				pass
			ingredients.append(ingred_string)
			del amount
			del unit
		
		return ingredients
	
	
	def print_recipe(self, verb_level=0):
		"""Print recipe to standard output."""
	
		print("")
		print(color.RECIPENAME + self.recipe_name + color.NORMAL)
		print("")
		
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


		print(S_DIV
			+ color.TITLE
			+ "\nIngredients:"
			+ color.NORMAL
			)
		
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
	
	
	def process_xml(self, mode="print", output_dir=RECIPE_XML_DIR):
		if self.check_file(silent=True):	
			# normal ingredients (i.e. not alternative ingredients as can be found below)
			xml_ingredients = etree.SubElement(self.root, "ingredients")
			for ingred in self.get_ingredients(): 	
				xml_ingred = etree.SubElement(xml_ingredients, "ingred")
				xml_ingred.text = ingred
			
			try:	
				print("im here")
				for item in self.alt_ingredients:
					xml_alt_ingredients = etree.SubElement(self.root, "alt_ingredients")
					xml_alt_ingredients.set('alt_name', item.title())
					
					for ingred in self.get_ingredients(alt_ingred=item):
						xml_alt_ingred = etree.SubElement(xml_alt_ingredients, "alt_ingred")
						xml_alt_ingred.text = ingred
			except AttributeError:
				print("but im also here and thats not good")
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
			
			
			if mode == "write":
				# file name vaiables
				recipe_name = self.recipe_name
				new_name = recipe_name.replace(" ", "_")
				lower_new_name  = new_name.lower() # I prefer file names to be all lower case
				# check for output dir flag	and make dir if it does not exist
				
				output_dir = os.path.abspath(output_dir)
				
				if os.path.exists(output_dir):
					if not os.path.isdir(output_dir):
						print("Not a directory")
						exit(1)
				else:
					try:
						os.makedirs(output_dir)
					except OSError:
						print("couldnt create directory")
						exit(1)
					
				print("{}Writing to file: {}/{}.xml{}".format(color.INFORM,
				                                              output_dir,
				                                              lower_new_name,
															  color.NORMAL)
				)
				with open(os.path.join(output_dir, lower_new_name) + ".xml", "w") as file:
					file.write(str(result.decode('utf-8')))
			
			if mode == "print":
				print(result.decode('utf-8'))
	
	
	def print_yaml(self):
		"""Print the recipe's source yaml. This can be helpful in troubleshooting"""
		
		PP.pprint(self.recipe_data)


class ShoppingList:
	"""Class to create and display a shopping list"""
	shopping_dict = {}
	recipe_names = []
	dressing_names = []

	
	def _proc_ingreds(self, source, alt_ingred=""):
		#TODO-> Serious flaw in this logic, work on it
		sd = ShoppingList.shopping_dict
		r = Recipe(source)
		if alt_ingred:
			ingred = r.alt_ingredient_data[alt_ingred]
		else:
			ingred = r.ingredient_data
		for item in ingred:
			name = item['name']
			if name == "s&p":
				continue
			amount = item['amounts'][0].get('amount', 0)
			unit = item['amounts'][0]['unit']
			# check if name already in sd so we can add together
			if name	in sd.keys():
				orig_amount = sd[name][0]
				orig_unit   = sd[name][1]	
				if orig_unit or unit in PINT_UNDEFINED_UNITS:
					print(orig_unit + unit)
					sys.exit('found offenders')
				if unit == orig_unit:
					orig = orig_amount * ureg(orig_unit)
					dup  = amount * ureg(unit)

					addition = orig + dup
					sd[name] = addition
				else:
					pass
			else:	
				sd[name] = [amount, unit]
	

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
		
		print("\n{}Writing shopping list to {}{}".format(color.INFORM, SHOPPING_LIST_FILE, color.NORMAL))
		with open(SHOPPING_LIST_FILE, "w") as f:
			f.write(result.decode("utf-8"))
	
	
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
		for key, value in sd.items():
			amount = value[0]
			if value[1] == "each":
				print(" {}, {}".format(key, value[0]))
				continue
			#if num > den:
			#	print("{}, {} {}".format(key, _improper_to_mixed(str(Fraction(amount))), value[1]))
			if amount == 0:
				print(" {}, {}".format(key, value[1]))
			elif amount < 1:
				print(" {}, {} {}".format(key, Fraction(amount), value[1]))
			elif amount > 1:
				#if type(amount) is float:
				#	print("{}, {} {}".format(key, _improper_to_mixed(Fraction(amount)), _plural(value[1])))
				#else:
				print(" {}, {} {}".format(key, Fraction(amount), _plural(value[1])))
			else:
				print(" {}, {} {}".format(key, Fraction(value[0]), value[1]))
			
		# write the list to an xml file	
		self.write_to_xml()


	def random_recipes(self, random_count=RAND_RECIPE_COUNT):
		"""Return random recipes and build a shopping list of ingredients needed"""	
		#TODO-> Use the shopping list class to make this shopping list too.

		sl = ShoppingList()
		try:
			recipe_sample = random.sample(MAINDISH_FILES, random_count)
			salad_dressing_random = random.choice(DRESSING_FILES)
		except ValueError:
			sys.exit("{}ERROR: Random count is higher than "
				     "the amount of recipes available ({}). "
				     "Please enter a lower number."
				     .format(color.ERROR, str(len(MAINDISH_FILES))))
		
		sl.update(salad_dressing_random)
		for dish in recipe_sample:
			sl.update(dish)
		
		self.print_list()
						



class DataBase:
	
	def __init__(self, db_file):
		self.db_file =	db_file

	def connect(self):
		conn = sqlite3.connect(db_file)
		c = conn.cursor()


###########
# functions
def template():
	"""Start the interactive template builder"""
	
	try:
		print("Interactive Template Builder. Press Ctrl-c to abort.\n")
		template = ""
		recipe_name = input("Enter recipe name: ")
		template += "recipe_name: {}\n".format(recipe_name)
		# check if file exist, lets catch this early so we can exit before entering in all the info
		new_name = recipe_name.replace(" ", "_")
		lower_new_name = new_name.lower() # I prefer file names to be all lower case
		file_name = RECIPE_DATA_DIR + lower_new_name + '.recipe'
		if os.path.isfile(file_name):
			print("File with this name already exist in directory exiting...")
			exit(1)
		while True:
			dish_type = input("Enter dish type: ")
			if dish_type not in DISH_TYPES:
				print("Dish type must be one of {}".format(", ".join(ALLOWED_DISH_TYPES)))
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


def gui_mode():
	"""Start recipe_tool in gui mode
	this function is currently under
	construction
	"""
	root = Tk()
	content = ttk.Frame(root)
	button = ttk.Button(content, text="Welcome to recipe tool")
	button.grid()
	text = Text(content, width="400", height="400")
	text.insert('1.0', "hello worldsssssssssssss")
	root.mainloop()


def list_recipes():
	"""List all recipes in the database"""
	
	recipe_files = os.listdir(RECIPE_DATA_DIR)
	recipe_list = []
	for item in recipe_files:
		abspath_file = RECIPE_DATA_DIR + item
		recipe = Recipe(abspath_file)
		recipename = recipe.recipe_name
		recipe_list.append(recipename)

	for item in sorted(recipe_list): print(item)


def edit_recipe(recipe_name):

	pass


def version():
	"""Print the current version of pyrecipe and exit."""

	print("{}                _              _              _ {}  {} v{}".format(color.INFORM, color.NORMAL, __scriptname__, __version__))
	print("{}               (_)            | |            | |{}  The recipe management program.".format(color.INFORM, color.NORMAL))
	print("{}  _ __ ___  ___ _ _ __   ___  | |_ ___   ___ | |{}".format(color.INFORM, color.NORMAL))
	print("{} | '__/ _ \/ __| | '_ \ / _ \ | __/ _ \ / _ \| |{}  For any questions, contact me at {}".format(color.INFORM, color.NORMAL, __email__))
	print("{} | | |  __/ (__| | |_) |  __/ | || (_) | (_) | |{}  or type recipe_tool --help for more info.".format(color.INFORM, color.NORMAL))
	print("{} |_|  \___|\___|_| .__/ \___|  \__\___/ \___/|_|{}".format(color.INFORM, color.NORMAL))
	print("{}                 | |                            {}  This program may be freely distributed under".format(color.INFORM, color.NORMAL))
	print("{}                 |_|                            {}  the terms of the GNU General Public Liscense.".format(color.INFORM, color.NORMAL))


def stats(verb=0):
	"""Print statistics about your recipe database and exit."""
	
	print("Recipes: {}".format(len(RECIPE_FILES)))
	if verb >= 1:
		print("Recipe directory: {}".format(RECIPE_DIR))
		print("Recipe xml directory: {}".format(RECIPE_XML_DIR))
		print("Default random recipe: {}".format(RAND_RECIPE_COUNT))



