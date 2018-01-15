# -*- encoding: UTF-8 -*-
"""
    pyrecipe.recipe
    ~~~~~~~~~~~~~~~
    The recipe module contains the main recipe
    class used to interact with ORF (open recipe format) files. 
    You can simply print the recipe or print the xml dump.

    - Recipe: The main recipe class is responsible for caching all the
              data associated with an Open Recipe Format file. Give the
              recipe instance an ORF source and all data can be accessed
              like a python dict. You can also assign new attributes or
              change current ones. Use the print_recipe() method to print
              the recipe to standard output and dump() to save the data
              back to the same file or one of your own choosing.
"""

import sys
from lxml import etree

from pyrecipe import utils
from pyrecipe import ureg, Q_, yaml, color
from pyrecipe.ingredient import Ingredient
from pyrecipe.config import (S_DIV)

class Recipe:
    """The recipe class is used to perform operations on
    recipe source files such as print and save xml.
    """
    # All keys applicable to the Open Recipe Format
    orf_keys = ['recipe_name', 'recipe_uuid', 'dish_type', 
                'category',    'cook_time',   'prep_time',       
                'author',      'oven_temp',   'bake_time',       
                'yields',      'ingredients', 'alt_ingredients', 
                'notes',       'url',         'steps']
    
    def __init__(self, source=''):
        self.source = source
        
        # Cache for the recipe data, if we start a class instance with a 
        # source, the data is cached in the next if statement
        self._recipe_data = {}
        
        if self.source: 
            self.source = utils.get_source_path(source)
            try:	
                with open(self.source, "r") as stream:
                    self._recipe_data = yaml.load(stream)
            except FileNotFoundError:
                sys.exit("{}ERROR: {} is not a file. Exiting..."
                         .format(color.ERROR, self.source))
        
        # All root keys included in the particular source which may
        # or may not include all keys from the orf spec
        self.yaml_root_keys = list(self._recipe_data.keys())
        
        # Scan the recipe to build the xml
        self._build_xml_tree()

    def __str__(self):
        """Returns the complete string representation of the recipe data."""
        recipe_string = '' 
        recipe_string += self['recipe_name'] + "\n"
        recipe_string += "\nIngredients:\n"
        
        # Put together all the ingredients
        for ingred in self.get_ingredients():	
            recipe_string += "{}\n".format(ingred)
        try:	
            for item in self['alt_ingredients']:
                recipe_string += "\n{}\n".format(item.title())
                for ingred in self.get_ingredients(alt_ingred=item):
                    recipe_string += "{}\n".format(ingred)
        except AttributeError:
                pass
        
        recipe_string += "\nMethod:\n"
        # print steps	
        for index, step in enumerate(self['steps'], start=1):
            recipe_string += "{}. {}\n".format(index, step['step'])
        return recipe_string

    def __getitem__(self, key):
        if key in __class__.orf_keys:
            return self.__dict__['_recipe_data'].get(key, '')
        else:
            return self.__dict__.get(key, '')

    def __setitem__(self, key, value):
        if key in __class__.orf_keys:
            self.__dict__['_recipe_data'][key] = value
            self._build_xml_tree()
        else:
            self.__dict__[key] = value

    def _build_xml_tree(self):
        """Internal method used to build the xml tree"""
        xml_root = etree.Element('recipe')
        # recipe name	
        if 'recipe_name' in self.yaml_root_keys:
            xml_recipe_name = etree.SubElement(xml_root, "name")
            xml_recipe_name.text = self['recipe_name']

        # recipe_uuid
        if 'recipe_uuid' in self.yaml_root_keys:
            xml_recipe_uuid = etree.SubElement(xml_root, "uuid")
            xml_recipe_uuid.text = str(self['recipe_uuid'])

        # dish_type
        if 'dish_type' in self.yaml_root_keys:
            xml_dish_type = etree.SubElement(xml_root, "dish_type")
            xml_dish_type.text = self['dish_type']
        
        # category
        if 'category' in self.yaml_root_keys:
            for entry in self['category']:
                xml_category = etree.SubElement(xml_root, "category")
                xml_category.text = str(entry)
        
        # author
        if 'author' in self.yaml_root_keys:
            xml_author = etree.SubElement(xml_root, "author")
            xml_author.text = self['author']

        # prep_time
        if 'prep_time' in self.yaml_root_keys:
            xml_prep_time = etree.SubElement(xml_root, "prep_time")
            xml_prep_time.text = str(self['prep_time'])

        # cook_time
        if 'cook_time' in self.yaml_root_keys:
            xml_cook_time = etree.SubElement(xml_root, "cook_time")
            xml_cook_time.text = str(self['cook_time'])

        # bake_time
        if 'bake_time' in self.yaml_root_keys:
            xml_bake_time = etree.SubElement(xml_root, "bake_time")
            xml_bake_time.text = str(self['bake_time'])

        # notes
        if 'notes' in self.yaml_root_keys:
            self.notes = self['notes']

        # price
        if 'price' in self.yaml_root_keys:
            xml_price = etree.SubElement(xml_root, "price")
            xml_price.text = str(self['price'])
        
        # oven_temp
        if 'oven_temp' in self.yaml_root_keys:
            self.oven_temp = self['oven_temp']
            self.ot_amount = self['oven_temp']['amount']
            self.ot_unit = self['oven_temp']['unit']
            xml_oven_temp = etree.SubElement(xml_root, "oven_temp")
            xml_oven_temp.text = str(self.ot_amount) + " " + str(self.ot_unit)
        
        # yields
        if 'yields' in self.yaml_root_keys:
            xml_yields = etree.SubElement(xml_root, "yields")
            for yeld in self['yields']:
                xml_servings = etree.SubElement(xml_yields, "servings")
                xml_servings.text = str(yeld)
        
        # ingredients
        xml_ingredients = etree.SubElement(xml_root, "ingredients")
        for ingred in self.get_ingredients(): 	
            xml_ingred = etree.SubElement(xml_ingredients, "ingred")
            xml_ingred.text = ingred
        
        # alt_ingredients
        if 'alt_ingredients' in self.yaml_root_keys:
            self.alt_ingredients = []
            # building a list of alternative ingredient names here helps later
            # in get_ingredients()
            for item in self['alt_ingredients'].keys():
                self.alt_ingredients.append(item)
        try:	
            for item in self['alt_ingredients']:
                xml_alt_ingredients = etree.SubElement(xml_root, "alt_ingredients")
                xml_alt_ingredients.set('alt_name', item.title())
                for ingred in self.get_ingredients(alt_ingred=item):
                    xml_alt_ingred = etree.SubElement(xml_alt_ingredients, "alt_ingred")
                    xml_alt_ingred.text = ingred
        except AttributeError:
                pass
        
        # steps	
        xml_steps = etree.SubElement(xml_root, "steps")
        for step in self['steps']:
            steps_of = etree.SubElement(xml_steps, "step")
            steps_of.text = step['step']
                
        result = etree.tostring(xml_root,
                                xml_declaration=True,
                                encoding='utf-8',
                                with_tail=False,
                                method='xml',
                                pretty_print=True).decode('utf-8')
        
        self.xml_data = result

    def get_ingredients(self, amount_level=0, alt_ingred=None):	
        """Returns a list of ingredients."""
        ingredients = []
        if alt_ingred:	
            ingredient_data = self['alt_ingredients'][alt_ingred]
        else:
            ingredient_data = self['ingredients']
        
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
            if self['bake_time']:
                print("Bake time: {} min.".format(str(self['bake_time'])))
            if self['oven_temp']:
                print("Oven temp: {} {}".format(str(self['oven_temp']['amount']), self['oven_temp']['unit']))
            if self['price']:
                print("Price: {}".format(self['price']))
        
        if verb_level >= 2:
            if self['author']:
                print("Author: {}".format(self['author']))
            if self['url']:
                print("URL: {}".format(self['url']))
            if self['category']:
                print("Category(s): " + ", ".join(self['category']))
            if self['yields']:
                print("Yields: " + str(self['yeilds']))
            if self['notes']:
                print(S_DIV)
                print("NOTES:")
                for note in self['notes']:
                    print(note)

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
        for index, step in enumerate(self['steps'], start=1):
            print("{}{}.{} {}".format(color.NUMBER, index, color.NORMAL, step['step']))

    def dump(self, stream=None):
        """Dump the yaml to a file or standard output""" 
        strm = self.source if stream is None else stream
        if strm == sys.stdout:
            yaml.dump(self['_recipe_data'], strm)
        else:
            with open(strm, 'w') as file: 
                yaml.dump(self['_recipe_data'], file)

# testing
if __name__ == '__main__':
    r = Recipe('egg rolls')
    #print(r.__dict__)
    print(r['url'])
    print(r['kjklj'])

    r.dump(stream=sys.stdout)

