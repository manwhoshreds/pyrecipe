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

              An instance of a recipe class contains all the information
              in a recipe.

              The current recipe data understood by the recipe class can
              be found in the class variable: orf_keys


    - RecipeWebScraper: The pyrecipe web_scraper class is a web
                        scraping utility used to download and analyze
                        recipes found on websites in an attempt to
                        save the recipe data in the format understood 
                        by pyrecipe.
                        Currently supported sites: www.geniuskitchen.com
    * Inherits from Recipe


    copyright: 2017 by Michael Miller
    license: GPL, see LICENSE for more details.
"""

import sys
import textwrap
from numbers import Number
from lxml import etree
from urllib.request import urlopen

import bs4

from pyrecipe import ureg, color, RecipeNum, yaml
from pyrecipe.ingredient import Ingredient, IngredientParser
from pyrecipe.config import (S_DIV, RECIPE_DATA_FILES, PP)
from pyrecipe.utils import get_source_path, mins_to_hours


class Recipe:
    """The recipe class is used to perform operations on
    recipe source files such as print and save xml.
    """
    # All keys applicable to the Open Recipe Format
    orf_keys = ['recipe_name', 'recipe_uuid', 'dish_type',
                'category',    'cook_time',   'prep_time',
                'author',      'oven_temp',   'bake_time',
                'yields',      'ingredients', 'alt_ingredients',
                'notes',       'source_url',  'steps',
                'tags',        'source_book', 'price']

    def __init__(self, source=''):
        self.source = source
        if self.source:
            self.source = get_source_path(source)

            try:
                with open(self.source, "r") as stream:
                    self._recipe_data = yaml.load(stream)
            except FileNotFoundError:
                sys.exit("{}ERROR: {} is not a file. Exiting..."
                         .format(color.ERROR, self.source))
        else:
            self._recipe_data = {}
            # dish type should default to main
            self['dish_type'] = 'main'

        # All root keys included in the particular source which may
        # or may not include all keys from the orf spec
        self.yaml_root_keys = list(self._recipe_data.keys())

        # Scan the recipe to build the xml
        self._scan_recipe()
    
    def __str__(self):
        """Returns the complete string representation of the recipe data."""
        recipe_string = ''
        recipe_string += self['recipe_name'] + "\n"
        recipe_string += "\nIngredients:\n"

        # Put together all the ingredients
        for ingred in self.get_ingredients():
            recipe_string += "{}\n".format(ingred)
        try:
            for item in self.alt_ingreds:
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

    def __repr__(self):
        return "<pyrecipe.recipe.Recipe object name='{}'>"\
                .format(self['recipe_name'])

    def __getitem__(self, key):
        if key in __class__.orf_keys:
            return self.__dict__['_recipe_data'].get(key, '')
        else:
            return self.__dict__.get(key, '')

    def __setitem__(self, key, value):
        if key == 'recipe_name':
            self.source = get_source_path(value)
        if key in __class__.orf_keys:
            self.__dict__['_recipe_data'][key] = value
            self._scan_recipe()
        else:
            self.__dict__[key] = value

    def _scan_recipe(self):
        """Internal method used to build the xml tree"""
        xml_root = etree.Element('recipe')
        # recipe name
        if self['recipe_name']:
            xml_recipe_name = etree.SubElement(xml_root, "name")
            xml_recipe_name.text = self['recipe_name']

        # recipe_uuid
        if self['recipe_uuid']:
            xml_recipe_uuid = etree.SubElement(xml_root, "uuid")
            xml_recipe_uuid.text = str(self['recipe_uuid'])

        # dish_type
        if self['dish_type']:
            xml_dish_type = etree.SubElement(xml_root, "dish_type")
            xml_dish_type.text = self['dish_type']

        # category
        if self['category']:
            for entry in self['category']:
                xml_category = etree.SubElement(xml_root, "category")
                xml_category.text = str(entry)

        # author
        if self['author']:
            xml_author = etree.SubElement(xml_root, "author")
            xml_author.text = self['author']

        # prep_time
        if self['prep_time']:
            xml_prep_time = etree.SubElement(xml_root, "prep_time")
            xml_prep_time.text = str(self['prep_time'])

        # cook_time
        if self['cook_time']:
            xml_cook_time = etree.SubElement(xml_root, "cook_time")
            xml_cook_time.text = str(self['cook_time'])

        # bake_time
        if self['bake_time']:
            xml_bake_time = etree.SubElement(xml_root, "bake_time")
            xml_bake_time.text = str(self['bake_time'])

        # ready_in
        # not actually an ord tag, so is not read from recipe file
        # it is simply calculated within the class
        if self['prep_time'] and self['cook_time']:
            self['ready_in'] = self['prep_time'] + self['cook_time']
        elif self['prep_time'] and self['bake_time']:
            self['ready_in'] = self['prep_time'] + self['bake_time']
        else:
            self['ready_in'] = self['prep_time']

        # notes
        if self['notes']:
            pass

        # price
        if self['price']:
            xml_price = etree.SubElement(xml_root, "price")
            xml_price.text = str(self['price'])

        # oven_temp
        if self['oven_temp']:
            self.oven_temp = self['oven_temp']
            self.ot_amount = self['oven_temp']['amount']
            self.ot_unit = self['oven_temp']['unit']
            xml_oven_temp = etree.SubElement(xml_root, "oven_temp")
            xml_oven_temp.text = str(self.ot_amount) + " " + str(self.ot_unit)

        # yields
        if self['yields']:
            xml_yields = etree.SubElement(xml_root, "yields")
            for yeld in self['yields']:
                xml_servings = etree.SubElement(xml_yields, "servings")
                xml_servings.text = str(yeld)

        # ingredients
        if self['ingredients']:
            xml_ingredients = etree.SubElement(xml_root, "ingredients")
            for ingred in self.get_ingredients():
                xml_ingred = etree.SubElement(xml_ingredients, "ingred")
                xml_ingred.text = ingred

        # alt_ingredients
        if self['alt_ingredients']:
            self.alt_ingreds = []
            # building a list of alternative ingredient names here helps later
            # in get_ingredients()
            for item in self['alt_ingredients']:
                test = list(item.keys())
                self.alt_ingreds += test
            try:
                for item in self.alt_ingreds:
                    xml_alt_ingredients = etree.SubElement(xml_root,
                                                           "alt_ingredients")
                    xml_alt_ingredients.set('alt_name', item.title())
                    for ingred in self.get_ingredients(alt_ingred=item):
                        xml_alt_ingred = etree.SubElement(xml_alt_ingredients,
                                                          "alt_ingred")
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

    @property
    def recipe_data(self):
        return self['_recipe_data']

    def get_ingredients(self, amount_level=0, alt_ingred=None):
        """Returns a list of ingredient strings.

        args:

        - amount_level: in aticipation of a future feature, this is for multiple
                        recipe yields.

        - alt_ingred: If an alt ingredient is given, it returns the ingredients
                      associated with the particular alt ingredient.
        """
        ingredients = []
        if alt_ingred:
            for item in self['alt_ingredients']:
                try:
                    ingredient_data = item[alt_ingred]
                except KeyError:
                    pass
        else:
            ingredient_data = self['ingredients']

        for item in ingredient_data:
            name = item['name']
            if name == 's&p':
                ingred = Ingredient('s&p')
                ingredients.append(str(ingred))
                continue
            amount = RecipeNum(item['amounts'][amount_level].get('amount', 0))
            unit = item['amounts'][amount_level].get('unit', '')
            size = item.get('size', '')
            prep = item.get('prep', '')
            ingred = Ingredient(name,
                                amount=amount.value,
                                size=size,
                                unit=unit,
                                prep=prep)
            ingredients.append(str(ingred))
        return ingredients

    def print_recipe(self, verb_level=0):
        """Print recipe to standard output."""
        print("\n"
            + color.RECIPENAME
            + self['recipe_name']
            + color.NORMAL
            + "\n")

        self['dish_type'] and print("Dish Type: {}"
                                    .format(str(self['dish_type'])))
        self['prep_time'] and print("Prep time: {}"
                                    .format(mins_to_hours(self['prep_time'])))
        self['cook_time'] and print("Cook time: {}"
                                    .format(mins_to_hours(self['cook_time'])))
        self['bake_time'] and print("Bake time: {}"
                                    .format(mins_to_hours(self['bake_time'])))
        self['ready_in'] and print("Ready in: {}"
                                   .format(mins_to_hours(self['ready_in'])))
        self['oven_temp'] and print("Oven temp: {} {}"
                                    .format(str(self['oven_temp']['amount']),
                                            self['oven_temp']['unit']))

        if verb_level >= 1:
            self['price'] and print("Price: {}".format(self['price']))
            self['author'] and print("Author: {}".format(self['author']))
            self['source_url'] and print("URL: {}".format(self['source_url']))
            self['category'] and print("Category(s): "
                                     + ", ".join(self['category']))
            self['yields'] and print("Yields: " + str(self['yeilds']))
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
            for item in self.alt_ingreds:
                print("\n{}{}{}".format(color.TITLE, 
                                        item.title(), 
                                        color.NORMAL))

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
        wrapper = textwrap.TextWrapper(width=60)
        wrapper.subsequent_indent = '   '
        for index, step in enumerate(self['steps'], start=1):
            if index >= 10:
                wrapper.subsequent_indent = '    '
            wrap = wrapper.fill(step['step'])
            print("{}{}.{} {}".format(color.NUMBER, index, color.NORMAL, wrap))
    
    def dump_yaml(self):
        """Dump the yaml data to standard output"""
        yaml.dump(self['_recipe_data'], sys.stdout)     
    
    def dump_xml(self):
        """Dump the xml data to standard output"""
        print(self['xml_data'])
    
    def dump(self, stream=None):
        """Dump the yaml to a file or standard output"""
        strm = self.source if stream is None else stream
        if strm == 'screen':
            yaml.dump(self['_recipe_data'], sys.stdout)
        else:
            if not self.source:
                raise RuntimeError('Recipe has no source to save to')
            if self.source in RECIPE_DATA_FILES:
                sys.exit('Recipe already exist with that file name.')
            with open(strm, 'w') as file:
                yaml.dump(self['_recipe_data'], file)


class RecipeWebScraper(Recipe):

    def __init__(self, url):
        super().__init__()
        self.scrapeable = False

        with open('web_scrapers.yaml', 'r') as stream:
            _scrapers = yaml.load(stream)

        self.scrapeable_sites = list(_scrapers.keys())
        for item in self.scrapeable_sites:
            if url.startswith(item):
                self.scrapeable = True
                self.site = item

        if not self.scrapeable:
            sys.exit('Site is not supported. Exiting...')

        self.rnt = _scrapers[self.site]['recipe_name_tag']
        self.rna = _scrapers[self.site]['recipe_name_attr']
        self.ilt = _scrapers[self.site]['ingred_list_tag']
        self.ila = _scrapers[self.site]['ingred_list_attr']

        self['source_url'] = url
        self.req = urlopen(url)
        self.soup = bs4.BeautifulSoup(self.req, 'html.parser')
        self._get_recipe_name()
        self._get_ingredients()
        self._get_author()
        self._get_method()

    def _get_recipe_name(self):
        name_box = self.soup.find(self.rnt, attrs=self.rna)
        self['recipe_name'] = name_box.text.strip()

    def _get_ingredients(self):
        ingred_box = self.soup.find_all(self.ilt, attrs=self.ila)
        ingred_parser = IngredientParser(return_dict=True)
        ingredients = []
        for item in ingred_box:
            for litag in item.find_all('li'):
                ingred_text = ' '.join(litag.text.strip().split())
                ingred = ingred_parser.parse(ingred_text)
                ingredients.append(ingred)
        self['ingredients'] = ingredients

    def _get_method(self):
        method_box = self.soup.find('div', attrs={'class': 'directions-inner container-xs'})
        litags = method_box.find_all('li')
        # last litag is "submit a correction", we dont need that
        del litags[-1]
        recipe_steps = []
        for item in litags:
            step_dict = {}
            step_dict['step'] = item.text.strip()
            recipe_steps.append(step_dict)

        self['steps'] = recipe_steps

    def _get_author(self):
        name_box = self.soup.find('h6', attrs={'class': 'byline'})
        recipe_by = name_box.text.strip()
        self['author'] = ' '.join(recipe_by.split(' ')[2:]).strip()


# testing
if __name__ == '__main__':
    # recipe
    r = Recipe('pot sticker dumplings')
    #r = Recipe()
    test = r.recipe_data
    #print(test)
    #r.dump_xml()
    r.dump_yaml()
    #r.dump('screen')
    #another = Recipe('7 cheese mac and cheese')
    #another.print_recipe()
    #r.print_recipe()
    #print(r)
    #print(r.xml_data)
    #r.dump(stream='sys.stdout')

    # recipewebscraper
    #scraper = RecipeWebScraper('http://www.geniuskitchen.com/recipe/pot-sticker-dipping-sauce-446277')
    #scraper = RecipeWebScraper('https://tasty.co/recipe/chicken-alfredo-lasagna')
    #scraper.scrape('http://www.geniuskitchen.com/recipe/bourbon-chicken-45809')
    #scraper.scrape('http://www.geniuskitchen.com/recipe/chicken-parmesan-19135')
    #scraper.scrape('http://www.geniuskitchen.com/recipe/stuffed-cabbage-rolls-29451')
    #scraper.print_recipe()
    #scraper.recipe.dump()
