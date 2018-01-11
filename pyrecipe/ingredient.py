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

from string import punctuation
from fractions import Fraction

from pyrecipe.config import (CAN_UNITS,
                             PREP_TYPES,
                             INGRED_UNITS,
                             SIZE_STRINGS)
from pyrecipe import utils


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
        self._amount = amount
        self.size = size
        self._unit = unit
        self.prep = prep
        
        self.name = self.get_name()
        self.amount = self.get_amount()
        self.unit = self.get_unit()
            
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
            string = "{} {} {} {}".format(self.amount, self.size, 
                                          self.unit, self.name)
            # the previous line adds unwanted spaces if values are absent
            # we simply clean that up here.
            cleaned_string = " ".join(string.split())
            if self.prep is '':
                return cleaned_string
            else:
                cleaned_string += ", " + self.prep
                return cleaned_string
                    
    def __add__(self, other):
        try:
            this = utils.num(self._amount) * ureg[self._unit]
            that = utils.num(other._amount) * ureg[other._unit]
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

    def get_name(self):
        if not self._unit or self._unit == 'each':
            return utils.p.plural(self._name, self._amount)
        else:
            return self._name

    def get_amount(self):
        if self._amount == .3:
            return '1/3'
        elif self._amount == .6:
            return '1/6'
        elif isinstance(self._amount, float) and self._amount < 1:
            return Fraction(self._amount)
        elif isinstance(self._amount, float) and self._amount > 1:
            return utils.improper_to_mixed(str(Fraction(self._amount)))
        else:
            return self._amount

    def get_unit(self):
        if self._unit == 'each':
            return ''
        elif utils.num(self._amount) > 1:
            if self._unit in CAN_UNITS:
                return "({})".format(utils.p.plural(self._unit))
            else:
                return utils.p.plural(self._unit)
        elif utils.num(self._amount) <= 1:
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

    """
    def __init__(self, string, return_dict=False):
        self.amount = ''
        self.size = ''
        self.unit = ''
        self.name = ''
        self.prep = ''
        self.ingred_dict = {}
        self.return_dict = return_dict
        
        # string preprocessing 
        self.strip_punc = self.strip_punctuation(string)
        self.raw_list = self.strip_punc.split()	
        self.lower_list = [x.lower() for x in self.raw_list]
        self.ingred_list = utils.all_singular(self.lower_list)
        
        for item in self.ingred_list:
            if re.search(r'\d+', item):
                self.amount = item
                self.ingred_list.remove(item)
                break
        
        for item in SIZE_STRINGS:
            if item in self.ingred_list:
                self.size = item
                self.ingred_list.remove(item)
        
        for item in INGRED_UNITS:	
            if item in self.ingred_list:
                self.unit = item
                self.ingred_list.remove(item)
        
        for item in PREP_TYPES:
            if item in self.ingred_list:
                self.prep = item
                self.ingred_list.remove(item)

        if not self.unit:
            self.unit = 'each'

        self.name = ' '.join(self.ingred_list)
        self.ingred_dict['amount'] = self.amount
        self.ingred_dict['size'] = self.size
        self.ingred_dict['unit'] = self.unit
        self.ingred_dict['name'] = self.name
        self.ingred_dict['prep'] = self.prep
        
        self.ingred_list = [self.amount, 
                            self.size, 
                            self.unit, 
                            self.name, 
                            self.prep]
    
    def __call__(self):
        if self.return_dict:
            return self.ingred_dict
        else:
            return self.ingred_list

    def strip_punctuation(self, string):
        return ''.join(c for c in string if c not in punctuation)
