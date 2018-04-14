"""
    pyrecipe.shopper
    ~~~~~~~~~~~~~~~~
    The shopper module allows you to build a shopping list of ingredients 
    from your recipes.

    - ShoppingList: The main shopper class 

    - RandomShoppingList: A ShoppingList subclass that chooses recipes at 
                          random an builds a shopping list.
    
    - MultiQuantity: A pint Quantity container that holds Quantities of
                     differing dimensionalities.
    
"""

import random
import datetime
import sys
from lxml import etree

import pint.errors

import pyrecipe.utils as utils
from pyrecipe.recipe_numbers import RecipeNum
from pyrecipe import Recipe, Q_, db, config

class ShoppingList:
    """Creates a shopping list of ingredients from a list of recipes. 
    
    If duplicate entries are found, ingredients are added together.
    """	
    def __init__(self):
        # Get xml ready
        self.xml_root = etree.Element('shopping_list')
        date = datetime.date
        today = date.today()
        date = etree.SubElement(self.xml_root, "date")
        date.text = str(today)
        self.xml_maindish_names = etree.SubElement(self.xml_root, "main_dishes")
        self.xml_salad_dressing = etree.SubElement(self.xml_root, "salad_dressing")
        self.xml_ingredients = etree.SubElement(self.xml_root, "ingredients")
        self.db_data = db.get_data()

        self.shopping_list = {}
        self.dressing_names = []
        self.recipe_names = []
    
    def _proc_ingreds(self, source, alt_ingred=""):
        sl = self.shopping_list
        r = Recipe(source)
        if alt_ingred:
            for item in r['alt_ingredients']:
                try:
                    ingreds = item[alt_ingred]
                except KeyError:
                    pass
        else:
            ingreds = r['ingredients']
        
        for item in ingreds:
            name = item['name']
            try:
                # links are recipe ingredients that are also 
                # recipes so we add it to the list here.
                link = item['link']
                self.update(link)
                if link:
                    continue
            except KeyError:
                pass
                    
            if name == "s&p":
                continue
            try:
                amount = RecipeNum(item['amounts'][0].get('amount', 0))
            except ValueError:
                amount = 0
            unit = item['amounts'][0].get('unit', '')
            if unit in ['splash of', 'to taste', 'pinch of']:
                continue
            
            # FIXME:
            # pint cannot handle units such as '16 ounce can' etc....
            # this is a workaround until a better solution is found
            if 'can' in unit:
                unit = 'can'
            try: 
                quant = Q_(amount, unit)
            except ValueError:
                print(amount, unit)
                exit()
            
            if name in sl.keys():
                orig_ingred = sl[name]
                try:
                    addition = orig_ingred + quant
                    sl[name] = addition
                except pint.errors.DimensionalityError:
                    sl[name] = MultiQuantity(orig_ingred, quant)
            else:
                sl[name] = quant

    def print_list(self, write=False):
        mdn = self.recipe_names
        sl = self.shopping_list
        dn = self.dressing_names
        
        print("Recipes:\n")
        for item in mdn:
            print(item)
        print("\n" + utils.S_DIV(45))

        if len(dn) > 0:
            print("Salad Dressings:\n")
            for item in dn:
                print(item)
            print("\n{}".format(utils.S_DIV(45)))
        
        # Print list	
        padding = max(len(x) for x in sl.keys()) + 1
        for key, value in sl.items():
            if value.units in ['splash of', 'to taste', 'pinch of']:
                print("{} {}".format(key.ljust(padding, '.'), 'N/A'))
            else:    
                try:
                    print("{} {}".format(key.ljust(padding, '.'), str(value.round_up())))
                except AttributeError:
                    print("{} {}".format(key.ljust(padding, '.'), value))

        # write the list to an xml file	if True
        if write:	
            self.write_to_xml()
    
    def write_to_xml(self):
        """Write the shopping list to an xml file after
           building.
        """
        # Add recipe names to the tree
        for item in self.recipe_names:
            xml_main_dish = etree.SubElement(self.xml_maindish_names, "name")
            xml_main_dish.text = str(item)
        
        # the salad dressing names
        for item in self.salad_dressings:
            xml_dressing_name = etree.SubElement(self.xml_salad_dressing, "name")
            xml_dressing_name.text = str(item)

        # finally, ingreds
        for key, value in self.shopping_list.items():
            try: 
                ingred = "{} {}".format(key, str(value.round_up()))
            except AttributeError:
                ingred = "{} {}".format(key, str(value))
            xml_shopping_list_item = etree.SubElement(self.xml_ingredients, "ingredient")
            xml_shopping_list_item.text = str(ingred)
                
        result = etree.tostring(self.xml_root,
                                xml_declaration=True,
                                encoding='utf-8',
                                with_tail=False,
                                method='xml',
                                pretty_print=True).decode("utf-8")
        
        utils.msg("Writing shopping list to %s" % config.SHOPPING_LIST_FILE, 'INFORM')
        with open(config.SHOPPING_LIST_FILE, "w") as f:
            f.write(result)
    
    def return_list(self):
        return self.shopping_list
    
    def update(self, source):

        r = Recipe(source)
        if r['dish_type'] == "salad dressing":
            self.dressing_names.append(r['recipe_name'])
        else:
            self.recipe_names.append(r['recipe_name'])

        
        self._proc_ingreds(source)
        alt_ingreds = r['alt_ingreds']
        if alt_ingreds:
            for item in alt_ingreds:
                self._proc_ingreds(source, alt_ingred=item)


class RandomShoppingList(ShoppingList):
    """The Random Shopping List class.

    Used to create a shopping list from a random sample of recipes
    given as an iterger argument.
    """
    
    def __init__(self, count=config.RAND_RECIPE_COUNT):
        super().__init__()
        self.count = count
        try:
            self.recipe_sample = random.sample(self.db_data['main_names'], self.count)
            self.salad_dressing_random = random.choice(self.db_data['salad_dressing_names'])
        except ValueError:
            sys.exit(utils.msg(
                "Random count is higher than the amount of recipes"
                " available ({}). Please enter a lower number."
                .format(len(self.db_data['main_names'])), "ERROR"
            ))
        self.update(self.salad_dressing_random)
        for dish in self.recipe_sample:
            self.update(dish)
    
    def print_random(self, write=False):
        self.print_list(write=write)


class MultiQuantity:
    """Class to deal with quantities of different dimentions"""

    def __init__(self, *args):
        self.quants = []
        self.type_test = type(Q_('1', 'teaspoon'))
        for item in args:
            if not isinstance(item, self.type_test):
                raise TypeError('arguments must be of type Quantity, '
                                'not ' + str(item))
            else:
                self.quants.append(item)

    def __str__(self):
        test = [str(x) for x in self.quants] 
        return ' + '.join(test)

    def __repr__(self):
        return '<MultiQuantity({})>'.format(self.quants)

    def __add__(self, other):
        if not isinstance(other, self.type_test):
            raise TypeError('Quantity types can only be added to MultiQuantity')
        for item in self.quants:
            try:
                addition = item + other
                self.quants.remove(item)
                self.quants.append(addition)
                break
            except pint.errors.DimensionalityError:
                continue
        return self
    
    @property
    def units(self):
        return 'n/a'

if __name__ == '__main__':
    test = db.get_data()
    config.PP.pprint(test)







