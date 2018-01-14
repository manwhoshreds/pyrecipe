# -*- encoding: UTF-8 -*-
"""
    pyrecipe.recipe
    ~~~~~~~~~~~~~~~
    The recipe module contains the main recipe
    classes used to interact with ORD (open recipe document) files. 
    You can simply print the recipe or print the xml dump.

    - Recipe: 
"""

import os
import sys
import re
import random
import sys
import subprocess
import datetime
from numbers import Number

from lxml import etree
#import sqlite3

from pyrecipe import utils
from pyrecipe import ureg, Q_, yaml
from pyrecipe.ingredient import *
from pyrecipe.config import (RAND_RECIPE_COUNT, RECIPE_DATA_DIR,
                     S_DIV)
# globals
color = utils.Color()

class Recipe:
    """The recipe class is used to perform operations on
    recipe source files such as print and save xml.
    """
    def __init__(self, source='', checkfile=True):
        self.source = source
        
        # Cache the recipe data
        self.xml_data = ''
        
        # All keys applicable to the Open Recipe Format
        self.orf_keys = ['recipe_name', 'recipe_uuid', 'dish_type', 
                         'category',    'cook_time',   'prep_time',       
                         'author',      'oven_temp',   'bake_time',       
                         'yields',      'ingredients', 'alt_ingredients', 
                         'notes']

        if self.source: 
            self.source = utils.get_source_path(source)
            try:	
                with open(self.source, "r") as stream:
                    self._recipe_data = yaml.load(stream)
            except FileNotFoundError:
                sys.exit("{}ERROR: {} is not a file. Exiting..."
                         .format(color.ERROR, self.source))
            
            # mainkeys
            self.mainkeys = list(self._recipe_data.keys())
            
            # finally scan the recipe
            self._build_xml_tree()

    def __str__(self):
        """Returns the complete string representation of the recipe data."""
        recipe_string = '' 
        recipe_string += self.recipe_name + "\n"
        recipe_string += "\nIngredients:\n"
        # Put together all the ingredients
        for ingred in self.get_ingredients():	
            recipe_string += "{}\n".format(ingred)
        try:	
            for item in self.alt_ingredients:
                recipe_string += "\n{}\n".format(item.title())
                for ingred in self.get_ingredients(alt_ingred=item):
                    recipe_string += "{}\n".format(ingred)
        except AttributeError:
                pass
        
        recipe_string += "\nMethod:\n"
        # print steps	
        for index, step in enumerate(self.steps, start=1):
            recipe_string += "{}. {}\n".format(index, step['step'])
        return recipe_string

    def __getitem__(self, key):
        if key in self.orf_keys:
            return self.__dict__['_recipe_data'].get(key, '')
        else:
            return self.__dict__.get(key, '')

    def __setitem__(self, key, value):
        if key in self.orf_keys:
            self.__dict__['_recipe_data'][key] = value
            self._build_xml_tree()
        else:
            self.__dict__[key] = value

    def _build_xml_tree(self):
        """Internal method used to build the xml tree"""
        self.xml_root = etree.Element('recipe')
        # recipe name	
        if 'recipe_name' in self.mainkeys:
            xml_recipe_name = etree.SubElement(self.xml_root, "name")
            xml_recipe_name.text = self['recipe_name']

        # recipe_uuid
        if 'recipe_uuid' in self.mainkeys:
            xml_recipe_uuid = etree.SubElement(self.xml_root, "uuid")
            xml_recipe_uuid.text = self['recipe_uuid']

        # dish_type
        if 'dish_type' in self.mainkeys:
            xml_dish_type = etree.SubElement(self.xml_root, "dish_type")
            xml_dish_type.text = self['dish_type']
        
        # category
        if 'category' in self.mainkeys:
            for entry in self['category']:
                xml_category = etree.SubElement(self.xml_root, "category")
                xml_category.text = str(entry)
        
        # author
        if 'author' in self.mainkeys:
            xml_author = etree.SubElement(self.xml_root, "author")
            xml_author.text = self['author']

        # prep_time
        if 'prep_time' in self.mainkeys:
            xml_prep_time = etree.SubElement(self.xml_root, "prep_time")
            xml_prep_time.text = str(self['prep_time'])

        # cook_time
        if 'cook_time' in self.mainkeys:
            xml_cook_time = etree.SubElement(self.xml_root, "cook_time")
            xml_cook_time.text = str(self['cook_time'])

        # bake_time
        if 'bake_time' in self.mainkeys:
            xml_bake_time = etree.SubElement(self.xml_root, "bake_time")
            xml_bake_time.text = str(self['bake_time'])

        # notes
        if 'notes' in self.mainkeys:
            self.notes = self._recipe_data['notes']

        # price
        if 'price' in self.mainkeys:
            xml_price = etree.SubElement(self.xml_root, "price")
            xml_price.text = str(self['price'])
        
        # oven_temp
        if 'oven_temp' in self.mainkeys:
            self.oven_temp = self._recipe_data['oven_temp']
            self.ot_amount = self._recipe_data['oven_temp']['amount']
            self.ot_unit = self._recipe_data['oven_temp']['unit']
            xml_oven_temp = etree.SubElement(self.xml_root, "oven_temp")
            xml_oven_temp.text = str(self.ot_amount) + " " + str(self.ot_unit)
        
        # yields
        if 'yields' in self.mainkeys:
            self.yields = self._recipe_data['yields']
            xml_yields = etree.SubElement(self.xml_root, "yields")
            for yeld in self.yields:
                xml_servings = etree.SubElement(xml_yields, "servings")
                xml_servings.text = str(yeld)

        if 'ingredients' in self.mainkeys:
            self.ingredient_data = self._recipe_data['ingredients']
        
        # alt_ingredients
        if 'alt_ingredients' in self.mainkeys:
            self.alt_ingredient_data = self._recipe_data['alt_ingredients']
            self.alt_ingredients = []
            # building a list of alternative ingredient names here helps later
            # in get_ingredients()
            for item in self.alt_ingredient_data.keys():
                self.alt_ingredients.append(item)
        
        # steps	
        if 'steps' in self.mainkeys:
            self.steps = self._recipe_data['steps']
        
        xml_ingredients = etree.SubElement(self.xml_root, "ingredients")
        for ingred in self.get_ingredients(): 	
            xml_ingred = etree.SubElement(xml_ingredients, "ingred")
            xml_ingred.text = ingred
        
        try:	
            for item in self.alt_ingredients:
                xml_alt_ingredients = etree.SubElement(self.xml_root, "alt_ingredients")
                xml_alt_ingredients.set('alt_name', item.title())
                for ingred in self.get_ingredients(alt_ingred=item):
                    xml_alt_ingred = etree.SubElement(xml_alt_ingredients, "alt_ingred")
                    xml_alt_ingred.text = ingred
        except AttributeError:
                pass
        
        steps = etree.SubElement(self.xml_root, "steps")

        for step in self.steps:
            steps_of = etree.SubElement(steps, "step")
            steps_of.text = step['step']
                
        result = etree.tostring(self.xml_root,
                                xml_declaration=True,
                                encoding='utf-8',
                                with_tail=False,
                                method='xml',
                                pretty_print=True).decode('utf-8')
        
        #self.xml_data = result

    def modify(self, attribute, new_attribute):
        self._recipe_data[attribute] = new_attribute
        self._build_xml_tree()
    
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
            unit = item['amounts'][amount_level].get('unit', '')
            size = item.get('size', '')
            prep = item.get('prep', '')
            ingred = Ingredient(name, unit=unit, amount=amount, size=size, prep=prep)
            ingredients.append(str(ingred))
        return ingredients
    
    def print_recipe(self, verb_level=0):
        """Print recipe to standard output."""

        print("\n"
            + color.RECIPENAME 
            + self['recipe_name']
            + color.NORMAL
            + "\n")
        
        if verb_level >= 1:
            if self['prep_time']:
                print("Prep time: {} min.".format(str(self['prep_time'])))
            
            if self['cook_time']:
                print("Cook time: {} min.".format(str(self['cook_time'])))
            try:
                print("Bake time: {} min.".format(str(self['bake_time'])))
            except AttributeError:
                pass
            try:
                print("Oven temp: {} {}".format(str(self['oven_temp']['amount']), self['oven_temp']['unit']))
            except AttributeError:
                pass
            try:
                print("Price: {}".format(self['price']))
            except AttributeError:
                pass 
        
        if verb_level >= 2:
            try:
                print("Author: {}".format(self['author']))
            except AttributeError:
                pass
            try:
                print("URL: {}".format(self['url']))
            except AttributeError:
                pass
            try:
                print("Category(s): " + ", ".join(self['category']))
            except AttributeError:
                pass
            try:
                print("Yields: " + str(self['yeilds']))
            except AttributeError:
                pass
            try:
                if self['notes']:
                    print(S_DIV)
                    print("NOTES:")
                    for note in self['notes']:
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
                + color.NORMAL)	
        
        # print steps	
        for index, step in enumerate(self.steps, start=1):
            print("{}{}.{} {}".format(color.NUMBER, index, color.NORMAL, step['step']))

    def dump(self, stream=None):
        """Dump the yaml to a file or standard output""" 
        strm = self.source if stream is None else stream
        if strm == sys.stdout:
            yaml.dump(self._recipe_data, strm)
        else:
            with open(strm, 'w') as file: 
                yaml.dump(self._recipe_data, file)

# testing
if __name__ == '__main__':
    r = Recipe('pesto')
    #r['recipe_name'] = 'dump'
    r['dish_type'] = 'nope'
    r['recipe_uuid'] = 928394797
    r.print_recipe()
    print(r['ingredients'][0]['name'])

    
    #print(r.__dict__)
    if r['kdjflkj']:
        print('oh yea bub')
    #r.dump(stream=sys.stdout)

