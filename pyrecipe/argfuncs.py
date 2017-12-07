"""
	pyrecipe.argfuncts
"""

#import os
import sys
import subprocess
from .config import PP

import pyrecipe.recipe as recipe
import pyrecipe.gui as gui

def dump_data(args):
	r = recipe.Recipe(args.source)

	if args.print_yaml:
		PP.pprint(r.recipe_data)
		exit(0)
	if args.print_xml:
		print(r.xml_data)
		exit(0)
	
def start_gui():
	gui.start()

def print_shopping_list(args):
	
	if args.random:
		rr = recipe.ShoppingList()
		rr.random_recipes(args.random)
	else:
		menu_items = args.recipes	
		if len(menu_items) == 0:
			sys.exit('You must supply at least one recipe'
					 ' to build your shopping list from!')
		
		sl = recipe.ShoppingList()
		
		for item in menu_items:
			sl.update(item)
				
		sl.print_list()


#def print_random_shopping_list(random_count):
#	rr = recipe.ShoppingList()
#	rr.random_recipes(random_count)

def check_file(args):
	if args.source == "all":
		for item in recipe.RECIPE_NAMES:
			r = recipe.Recipe(item)
			r.check_file()
	else:
		r = recipe.Recipe(args.source)
		r.check_file()
	



def print_recipe(args):
	r = recipe.Recipe(args.source)
	r.print_recipe(args.verbose)


def show_stats(args):
	recipe.stats(args.verbose)

def delete_recipe(args):
	import os
	source = args.source
	file_name = str(recipe.Recipe(source))
	answer = input("Are you sure your want to delete {}? yes/no ".format(source))
	if answer.strip() == 'yes':
		os.remove(file_name)
	else:
		print("{} not deleted".format(source))



def edit_recipe(args):
	if args.source.title() not in recipe.list_recipes(ret=True):
		print("No recipe found for {}".format(args.source))
	else:
		file_name = args.source.replace(" ", "_").lower() + ".recipe"
		abspath_file_name = recipe.RECIPE_DATA_DIR + file_name
		subprocess.call([recipe.EDITOR, abspath_file_name])

def add_recipe(args):
	if args.name.title() in recipe.list_recipes(ret=True):
		sys.exit('A recipe with that name already exist in the recipe store')
	else:
		recipe.template(args.name)


def print_list(args):
	recipe.list_recipes()


def version(args):
	recipe.version()


def export_recipes(args):
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
