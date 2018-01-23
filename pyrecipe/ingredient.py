# -*- coding: utf-8 -*-
"""
    pyrecipe.ingredient
    ~~~~~~~~~~~~~~~~~~~

    This module contains all classes used for the processing of ingredient
    related data. 
    
    - Ingredient: Returns a gramatically correct ingredient string given
                  the elments of ingredient data
        
    - IngredientParser: Converts an ingredient string into a list of ingredient
                        data elements. 

    :copyright: 2018 by Michael Miller
    :license: GNU General Public License
"""
import re
from fractions import Fraction

from pint.errors import (DimensionalityError)

from pyrecipe import ureg, Q_, RecipeNum, p
from pyrecipe import utils
from pyrecipe.config import (CAN_UNITS,
                             PREP_TYPES,
                             INGRED_UNITS,
                             SIZE_STRINGS)


class Ingredient:
    """The ingredient class is used to build an ingredietns object
    
    :param name: name of the ingredient e.g onion
    :param amount: amount of ingredient
    :param size: size of ingredient
    :param unit: ingredient unit such as tablespoon
    :param prep: prep string if any, such as diced, chopped.. etc...
    """
    def __init__(self, name, amount=0, size='', unit='', prep=''):
        self._name = name
        self._amount = RecipeNum(amount)
        self._size = size
        self._unit = unit
        self._prep = prep
        
    def __str__(self):
        """Turn ingredient object into a string
        
        Calling string on an ingredient object returns the gramatically
        correct representation of the ingredient object.
        """
        if self._name == 's&p':
                return "Salt and pepper to taste"
        elif self._unit == 'taste':
                return "{} to taste".format(self._name.capitalize())
        elif self._unit == 'pinch':
                return "Pinch of {}".format(self._name)
        elif self._unit == 'splash':
                return "Splash of {}".format(self._name)
        else:
            string = "{} {} {} {}".format(self.amount, self._size, 
                                          self.unit, self.name)
            # the previous line adds unwanted spaces if values are absent
            # we simply clean that up here.
            cleaned_string = " ".join(string.split())
            if self._prep is '':
                return cleaned_string
            else:
                cleaned_string += ", " + self._prep
                return cleaned_string
                    
    def __add__(self, other):
        #TODO: FIX THIS FUNCTION
        # as it currently stands, if this function encounters
        # pints DimensionalityError, (the addition of two quantities whose
        # units are incompatible and cannot be added together), we pretty
        # mush abort and just send back the unaltered inputs from self.
        try:
            this = self._amount.value * ureg[self._unit]
            that = other._amount.value * ureg[other._unit]
            # the following is just is a workaround for pints addition behaviour
            # if pint returns a float we have to switch the components of the addition
            # statement in order to get back a whole number
            addition = this + that
            if isinstance(addition.magnitude, float):
                if addition.magnitude.is_integer():
                    string = str(addition).split()
                else:
                    addition = that + this
                    string = str(addition).split()
                return [string[0], string[1]]
            else:
                string = str(addition).split()
                return [string[0], string[1]]
        except DimensionalityError:
            return [self._amount.value, self._unit]

    def __getitem__(self, key):
        return self.__dict__[key]
    
    @property
    def name(self):
        if not self._unit or self._unit == 'each':
            return p.plural(self._name, self._amount.value)
        else:
            return self._name
    
    @property
    def amount(self):
        # cannont figure out how to let python handle irrational numbers. which are
        # quite prevalant in recipe data. ( think 1/3, 1/6 etc... )
        # here is a functional work-around
        third = re.compile('^0.3|^.3')
        sixth = re.compile('^0.6|^.6')
        eighth = re.compile('^0.125|^.125')
        if third.match(str(self._amount.value)):
            return '1/3'
        elif sixth.match(str(self._amount.value)):
            return '1/6'
        elif eighth.match(str(self._amount.value)):
            return '1/8'
        elif isinstance(self._amount.value, float) and self._amount.value < 1:
            return Fraction(self._amount.value)
        elif isinstance(self._amount.value, float) and self._amount.value > 1:
            return utils.improper_to_mixed(str(Fraction(self._amount.value)))
        else:
            return self._amount.value
    
    @property 
    def unit(self):
        if self._unit == 'each':
            return ''
        elif self._amount.value > 1:
            if self._unit in CAN_UNITS:
                return "({})".format(p.plural(self._unit))
            else:
                return p.plural(self._unit)
        elif self._amount.value <= 1:
            if self._unit in CAN_UNITS:
                return "({})".format(self._unit)
            else:
                return self._unit
        else:
            return self._unit


class IngredientParser:
    """Convert an ingredient string into a list or dict

    an excepted ingredient string is usually in the form of
    
    "<amount> <size> <unit> <ingredient>, <prep>"
    
    however, not all elements of an ingredient string may
    be present in every case. It is the job of the ingredient
    parser to identify what an ingredient string contains, and to 
    return a list or dict populated with the relevant data.

    params:
    
    - return_dict: return ingredient data in a dict in the form of
                   {'name': <name>,
                    'size': <size>,
                    'amount': <amount>,
                    'prep': <prep>}
    """
    def __init__(self, return_dict=False):
        self.return_dict = return_dict
        self.punctuation = "!\"#$%&'()*+,-:;<=>?@[\]^_`{|}~"

    def parse(self, string=''):
        amount = 0
        size = ''
        unit = ''
        name = ''
        prep = ''
        ingred_list = []
        ingred_dict = {}
        #numbermatch = re.compile(r'[0-9]|[0-9]*[\/]*[0-9]')
        
        # string preprocessing 
        self.strip_punc = self._strip_punctuation(string)
        raw_list = self.strip_punc.split()	
        lower_list = [x.lower() for x in raw_list]
        ingred_list = utils.all_singular(lower_list)
        
        amnt_list = [] 
        for item in ingred_list:
            if RecipeNum(item).isnumber:
                amnt_list.append(item)
                ingred_list.remove(item)

        amount = ' '.join(amnt_list)
        
        for item in SIZE_STRINGS:
            if item in ingred_list:
                size = item
                ingred_list.remove(item)
        
        for item in INGRED_UNITS:	
            if item in ingred_list:
                unit = item
                ingred_list.remove(item)
        
        for item in PREP_TYPES:
            if item in ingred_list:
                prep = item
                ingred_list.remove(item)

        if not unit:
            unit = 'each'
            
        # at this point we are assuming that all elements have been removed
        # from list except for the name. Whatever is left gets joined together
        name = ' '.join(ingred_list)
        if name.lower == 'salt and pepper':
            name = 's&p'
        ingred_dict['amounts'] = [{'amount': amount, 'unit': unit}]
        ingred_dict['size'] = size
        ingred_dict['name'] = name
        ingred_dict['prep'] = prep
        
        ingred_list = [amount, size, unit, name, prep]

        if self.return_dict:
            return ingred_dict
        else:
            return ingred_list
    
    def _strip_punctuation(self, string):
        return ''.join(c for c in string if c not in self.punctuation)

# testing
if __name__ == '__main__':
    #i = IngredientParser(return_dict=True)
    #test = i.parse('2 1/2 tablespoons onion, chopped')
    #print(test)
    test = RecipeNum('test')

    #ingred = Ingredient('onion', .3, 'large', 'tablespoon', 'chopped')
    #print(str(ingred))
