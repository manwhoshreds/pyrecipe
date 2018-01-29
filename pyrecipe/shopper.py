"""
    pyrecipe.shopper
    ~~~~~~~~~~~~~~~~

    build a shopping list of ingredients from your recipes

"""
import random
import datetime
import sys
from fractions import Fraction
from lxml import etree

from pint.errors import (DimensionalityError)

from pyrecipe.config import (RAND_RECIPE_COUNT, S_DIV,
                             SHOPPING_LIST_FILE)
from pyrecipe.recipe import Recipe, Ingredient
from pyrecipe import manifest, color, RecipeNum, Q_

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

        self.shopping_dict = {}
        self.shopping_list = []
        self.recipe_names = []
        self.dressing_names = []
        
    def _proc_ingreds(self, source, alt_ingred=""):
        sd = self.shopping_dict
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
            amount = RecipeNum(item['amounts'][0].get('amount', 0))
            unit = item['amounts'][0].get('unit', '')
            try: 
                quant = Q_(amount, unit)
            except ValueError:
                quant = Q_('1', 'teaspoon')
                print("%s is not a good unit!" % unit)
            # check if name already in sd so we can add together
            if name in sd.keys():
                try:
                    print("look out for: " + name) 
                    try:
                        orig_ingred = Q_(RecipeNum(sd[name][0]), sd[name][1])
                    except ValueError:
                        orig_ingred = Q_('1', 'teaspoon')
                        print("%s is not a good unit!" % unit)

                    addition = orig_ingred + quant
                    sd[name] = str(addition).split()
                except DimensionalityError:
                    sd[name] = [orig_ingred, quant]
                    print("canot add: " + repr(orig_ingred) + " + " + repr(quant))
            else:
                try:
                    sd[name] = str(quant).split()
                except ValueError:
                    print("offenders: " + name, amount, unit)

    def write_to_xml(self):
        """Write the shopping list to an xml file after
           building.
        """
        # Add recipe names to the tree
        for item in self.recipe_names:
            xml_main_dish = etree.SubElement(self.xml_maindish_names, "name")
            xml_main_dish.text = str(item)
        
        # the salad dressing names
        for item in self.dressing_names:
            xml_dressing_name = etree.SubElement(self.xml_salad_dressing, "name")
            xml_dressing_name.text = str(item)

        # finally, ingreds
        for key, value in self.shopping_dict.items():
            ingred = "{} {} {}".format(key, str(value[0]), str(value[1]))
            xml_shopping_list_item = etree.SubElement(self.xml_ingredients, "ingredient")
            xml_shopping_list_item.text = str(ingred)
                
        result = etree.tostring(self.xml_root,
                                xml_declaration=True,
                                encoding='utf-8',
                                with_tail=False,
                                method='xml',
                                pretty_print=True).decode("utf-8")
        
        print("\n{}Writing shopping list to {}{}".format(color.INFORM, SHOPPING_LIST_FILE, color.NORMAL))
        with open(SHOPPING_LIST_FILE, "w") as f:
            f.write(result)
    
    def return_list(self):
        return self.shopping_dict
    
    def update(self, source):

        r = Recipe(source)
        if r['dish_type'] == "salad dressing":
            self.dressing_names.append(r['recipe_name'])
        else:
            self.recipe_names.append(r['recipe_name'])

        
        self._proc_ingreds(source)
        try:
            alt_ingreds = r['alt_ingreds']
            for item in alt_ingreds:
                self._proc_ingreds(source, alt_ingred=item)
        except AttributeError:
            pass
        
    def print_list(self, write=False):
        mdn = self.recipe_names
        sd = self.shopping_dict
        #print(sd)
        dn = self.dressing_names
        
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
            print("{}, {} {}".format(key, value[0], value[1]))
        # write the list to an xml file	if True
        if write:	
            self.write_to_xml()
                

class RandomShoppingList(ShoppingList):
    """The Random Shopping List class

    Used to create a shopping list from 
    a random sample of recipes
    given as an iterger argument.
    """
    
    def __init__(self, count=RAND_RECIPE_COUNT):
        super().__init__()
        self.count = count
        try:
            self.recipe_sample = random.sample(manifest.maindish_names, self.count)
            self.salad_dressing_random = random.choice(manifest.dressing_names)
        except ValueError:
            sys.exit("{}ERROR: Random count is higher than "
                     "the amount of recipes available ({}). "
                     "Please enter a lower number."
                     .format(color.ERROR, str(len(manifest.maindish_names))))
        
        self.update(self.salad_dressing_random)
        for dish in self.recipe_sample:
            self.update(dish)
    
    def print_random(self):
        self.print_list()

# testing
if __name__ == '__main__':
    shopper = ShoppingList()    
    shopper.update('pesto')
    shopper.update('pot sticker dumplings')
    test = shopper.return_list()
    print(test)





