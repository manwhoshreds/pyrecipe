# -*- coding: utf-8 -*-
"""
    pyrecipe.ingredient
    ~~~~~~~~~~~~~~~~~~~

    This module contains all classes used for the processing of ingredient
    related data. 
    
    - Ingredient: Returns a gramatically correct ingredient string given
                  the elments of ingredient data
        
    - IngredientParser: Converts an ingredient string into a list or dict 
                        of ingredient data elements. 

    :copyright: 2018 by Michael Miller
    :license: GNU General Public License
"""
import re
from fractions import Fraction

from pint.errors import (DimensionalityError)

from pyrecipe import ureg, Q_, p
from pyrecipe import utils
from pyrecipe.recipe_numbers import Mixed, RecipeNum
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
        try: 
            self._amount = Mixed(amount)
        except ValueError:
            self._amount = 0
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
            this = self._amount * ureg[self._unit]
            that = other._amount * ureg[other._unit]
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
            return [self._amount, self._unit]

    def __getitem__(self, key):
        return self.__dict__[key]
    
    @property
    def name(self):
        if not self._unit or self._unit == 'each':
            return p.plural(self._name, self._amount)
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
        if third.match(str(self._amount)):
            return '1/3'
        elif sixth.match(str(self._amount)):
            return '1/6'
        elif eighth.match(str(self._amount)):
            return '1/8'
        elif isinstance(self._amount, float) and self._amoun < 1:
            return Fraction(self._amount)
        elif isinstance(self._amount, float) and self._amount > 1:
            return str(Mixed(str(Fraction(self._amount))))
        else:
            return self._amount
    
    @property 
    def unit(self):
        if self._unit == 'each':
            return ''
        elif self._amount > 1:
            if self._unit in CAN_UNITS:
                return "({})".format(p.plural(self._unit))
            else:
                return p.plural(self._unit)
        elif self._amount <= 1:
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
                    'amounts': [{'amount': <amount>, 'uniit': <unit>}]
                    'prep': <prep>}

    examples:

    >>> parser = IngredientParser()
    >>> parser.parse('1 tablespoon onion, chopped') 
    [1, '', 'tablespoon', 'onion chopped', 'chopped']
    >>> parser.parse('3 large carrots, finely diced')
    ['3', 'large', 'carrot', 'finely diced']
    >>> parser = IngredientParser(return_dict=True)
    >>> parser.parse('1 tablespoon onion chopped')
    {'amounts': [{'amount': 1, 'unit': 'tablespoon'}],\ 
     'name': 'onion chopped', 'prep': 'chopped'}
    """
    def __init__(self, return_dict=False):

        self.return_dict = return_dict
        self.punctuation = "!\"#$%&'()*+,-:;<=>?@[\]^_`{|}~"
        self._OUNCE_CAN_RE = re.compile(r'\d+ (ounce|pound) (can|bag)')
        self._PAREN_RE = re.compile(r'\((.*?)\)')
    
    def _preprocess_string(self, string):
        """preprocess the string""" 
        # this special forward slash character (differs from '/') is encounterd
        # on some sites througout the web. There maybe others
        if '⁄' in string:
            string = string.replace('⁄', '/')
        test = self._PAREN_RE.search(string)
        if test:
            print(test.group())
        stripd_punc = self._strip_punctuation(string).lower()
        singular_string = ' '.join(utils.all_singular(stripd_punc.split()))
        return singular_string


    def parse(self, string=''):
        """parse the ingredient string"""
        amount = ''
        size = ''
        unit = ''
        name = ''
        prep = ''
        ingred_list = []
        ingred_dict = {}
        
        # string preprocessing 
        pre_string = self._preprocess_string(string)
        match = self._OUNCE_CAN_RE.search(pre_string)
        if match:
            pre_string = pre_string.replace(match.group(), '')
            unit = match.group()
        
        ingred_list = pre_string.split() 
        amnt_list = [] 
        for item in ingred_list:
            try:
                Mixed(item)
                amnt_list.append(item)
            except ValueError:
                continue
       
        try:
            amount = str(Mixed(' '.join(amnt_list)))
        except ValueError:
            amount = ''
        
        ingred_list = [x for x in ingred_list if x not in amnt_list]
        ingred_string = ' '.join(ingred_list)

        
        for item in SIZE_STRINGS:
            if item in ingred_string:
                size = item
                ingred_string = ingred_string.replace(item, '')
        
        for item in INGRED_UNITS:	
            if item in ingred_string:
                unit = item
                ingred_string = ingred_string.replace(item, '')
        
        for item in PREP_TYPES:
            if item in ingred_string:
                prep = item
                ingred_string = ingred_string.replace(item, '')
                print(ingred_string)

        if not unit:
            unit = 'each'
            
        # at this point we are assuming that all elements have been removed
        # from list except for the name. Whatever is left gets joined together
        name = ' '.join(ingred_string.split())
        if name.lower == 'salt and pepper':
            name = 's&p'
        ingred_dict['amounts'] = [{'amount': amount, 'unit': unit}]
        if size: ingred_dict['size'] = size
        ingred_dict['name'] = name
        if prep: ingred_dict['prep'] = prep
        
        ingred_list = [amount, size, unit, name, prep]

        if self.return_dict:
            return ingred_dict
        else:
            return ingred_list
    
    def _strip_punctuation(self, string):
        return ''.join(c for c in string if c not in self.punctuation)

# testing
if __name__ == '__main__':
    #import doctest
    #doctest.testmod()
    i = IngredientParser(return_dict=True)
    test = i.parse('2 1/2 12 ouNce cans onion, chopped')
    #test = Mixed('1 1/2')
    #print(test)



    #ingred = Ingredient('onion', .3, 'large', 'tablespoon', 'chopped')
    #print(str(ingred))
