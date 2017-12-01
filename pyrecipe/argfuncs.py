"""
	pyrecipe.argfuncts
"""

import os
import sys
import subprocess

import pyrecipe.recipe as recipe

def dump_data(args):
	r = recipe.Recipe(args.source)

	if args.print_yaml:
		r.print_yaml()
		exit(0)
	if args.print_xml:
		r.process_xml()
		exit(0)
	

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
	if args.source not in recipe.list_recipes(ret=True):
		print("No recipe found for {}".format(args.source))
	else:
		r = recipe.Recipe(args.source)
		r.print_recipe(args.verbose)


def show_stats(args):
	recipe.stats(args.verbose)

def delete_recipe(args):
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


def export_recipes(args):
	pass
