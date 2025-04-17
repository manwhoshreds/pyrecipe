import re
from dataclasses import dataclass
import re
import os
import sys
import json
import string
from typing import List
from copy import deepcopy
from zipfile import ZipFile, BadZipFile
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict

from pyrecipe import utils
from pyrecipe import Quant, CULINARY_UNITS
from pyrecipe.backend.recipe_numbers import RecipeNum

@dataclass
class ParsedIngredient:
    quantity: str
    unit: str
    ingredient: str
    preparation: str
    note: str

class IngredientParser:
    def __init__(self, model=None):
        """If model is provided, use AI model, else fallback to rule-based."""
        self.model = model

    def parse(self, ingredient_string):
        if self.model:
            return self._parse_with_model(ingredient_string)
        else:
            return self._parse_with_rules(ingredient_string)

    def _parse_with_rules(self, ingredient_string):
        """A very primitive rule-based parser to prototype structure."""
        pattern = r"(?P<quantity>\d+[\d\/\s\.]*)?\s*(?P<unit>[a-zA-Z]+)?\s*(?P<prep>(chopped|diced|minced|sliced|ground|freshly|optional|to taste|drained) )?(?P<ingredient>[a-zA-Z\s]+)(, (?P<note>.*))?"
        
        match = re.match(pattern, ingredient_string, re.IGNORECASE)
        if match:
            return ParsedIngredient(
                quantity=match.group("quantity") or "",
                unit=match.group("unit") or "",
                ingredient=match.group("ingredient").strip(),
                preparation=match.group("prep") or "",
                note=match.group("note") or ""
            )
        else:
            # fallback — if parsing fails
            return ParsedIngredient(
                quantity="",
                unit="",
                ingredient=ingredient_string,
                preparation="",
                note=""
            )

    def _parse_with_model(self, ingredient_string):
        """Uses AI model for parsing (not implemented yet)"""
        # model should return a dict with the necessary fields
        result = self.model(ingredient_string)
        return ParsedIngredient(**result)

parser = IngredientParser()
test = parser.parse("1 tablespoon fresh oregano, chopped")


class Ingredient:
    """Build an Ingredient object.

    :param ingredient: dict or string of ingredient.
    """
    PORTIONED_UNIT_RE = re.compile(r'\(?\d+\.?\d*? (ounce|pound)\)? (cans?|bags?)')
    PAREN_RE = re.compile(r'\((.*?)\)')
    SIZE_STRINGS = ['large', 'medium', 'small', 'heaping']
    PUNCTUATION = ''.join(c for c in string.punctuation if c not in '-/(),.')

    def __init__(self, ingredient):
        self.amount, self.portion, self.size, self.name = ('',) * 4
        self.unit, self.prep, self.note, self.group_name = ('',) * 4
        if isinstance(ingredient, str):
            self.parse_ingredient(ingredient)
        else:
            self.group_name = ingredient.get('group_name', None)
            if self.amount:
                self.amount = RecipeNum(self.amount)
            self.amount = ingredient.get('amount', '')
            self.size = ingredient.get('size', None)
            self.portion = ingredient.get('portion', None)
            self.unit = ingredient.get('unit', None)
            self.name = ingredient['name']
            self.prep = ingredient.get('prep', None)
            self.note = ingredient.get('note', None)


    def __repr__(self):
        return f"<Ingredient('{self.name}')>"


    def __str__(self):
        """Turn ingredient object into a string

        Calling string on an ingredient object returns the gramatically
        correct representation of the ingredient object.
        Though not every ingredients will have all parts, a full ingredient
        string will look like this:

        <amt> <size> <unit>  <name>       <prep>  <note>
        1 heaping tablespoon cumin seeds, toasted (you may use cumin powder)
        """
        ingred_string = []
        if self.unit == 'taste':
            string = "{} to taste".format(self.name.capitalize())
            ingred_string.append(string)
        elif self.unit == 'pinch':
            string = "pinch of {}".format(self.name)
            ingred_string.append(string)
        elif self.unit == 'splash':
            string = "splash of {}".format(self.name)
            ingred_string.append(string)
        else:
            # amnt
            if self.amount:
                ingred_string.append('{}'.format(self.amount))
            # size
            if self.size:
                ingred_string.append(' {}'.format(self.size))
            # portion
            if self.portion:
                ingred_string.append(' ({})'.format(self.portion))
            # unit
            if self.unit:
                if self.unit == 'each':
                    pass
                else:
                    ingred_string.append(' {}'.format(self.unit))

            # name
            ingred_string.append(' {}'.format(self.name))

        if self.prep:
            ingred_string.append(", " + self.prep)
        if self.note:
            note = ' ({})'.format(self.note)
            ingred_string.append(note)
        string = ''.join(ingred_string).strip().capitalize()
        return string

    def _preprocess_string(self, string):
        """preprocess the string"""
        # this special forward slash character (differs from '/') is encounterd
        # on some sites througout the web. There maybe others
        if '⁄' in string:
            string = string.replace('⁄', '/')
        unicode_fractions = {
            '¼': '1/4',
            '½': '1/2',
            '⅓': '1/3',
            '¾': '3/4'
        }
        for frac in unicode_fractions.keys():
            if frac in string:
                string = string.replace(frac, unicode_fractions[frac])

        lower_stripd_punc = self._strip_punct(string).lower()
        return lower_stripd_punc

    def _strip_parens(self, string):
        return ''.join(c for c in string if c not in ('(', ')'))

    def _strip_punct(self, string):
        return ''.join(c for c in string if c not in self.PUNCTUATION)

    @property
    def quantity(self):
        """get the quantity"""
        unit = self.unit
        if not self.unit:
            unit = 'each'
        match = self.PORTIONED_UNIT_RE.search(unit)
        if match:
            unit = match.group().split()
            self.ounce_can = unit[0:2]
            self.amount = 1
            unit = unit[-1]
        return Quant(RecipeNum(self.amount), unit)

    def parse_ingredient(self, string):
        """parse the ingredient string"""
        ingred_string = self._preprocess_string(string)
        # get unit
        match = self.PORTIONED_UNIT_RE.search(ingred_string)
        if match:
            ingred_string = ingred_string.replace(match.group(), '')
            unit = self._strip_parens(match.group()).split()
            self.portion = ' '.join(unit[:2])
            self.unit = unit[-1]
        else:
            if "to taste" in ingred_string:
                self.unit = "taste"
                ingred_string = ingred_string.replace("to taste", '')
            elif "splash of" in ingred_string:
                self.unit = "splash"
                ingred_string = ingred_string.replace("splash of", '')
            elif "pinch of" in ingred_string:
                self.unit = "pinch"
                ingred_string = ingred_string.replace("pinch of", '')
            else:
                for item in CULINARY_UNITS:
                    if item in ingred_string.split():
                        self.unit = item
                        ingred_string = ingred_string.replace(item, '')

        # get note if any
        parens = self.PAREN_RE.search(ingred_string)
        if parens:
            ingred_string = ingred_string.replace(parens.group(), '').strip()
            self.note = self._strip_parens(parens.group())

        ingred_list = ingred_string.split()
        amnt_list = []
        for item in ingred_list:
            try:
                RecipeNum(item)
                amnt_list.append(item)
            except ValueError:
                continue
        try:
            self.amount = str(RecipeNum(' '.join(amnt_list)))
        except ValueError:
            self.amount = None


        ingred_list = [x for x in ingred_list if x not in amnt_list]
        ingred_string = ' '.join(ingred_list)

        for item in self.SIZE_STRINGS:
            if item in ingred_string:
                self.size = item
                ingred_string = ingred_string.replace(item, '')

        for item in CULINARY_UNITS:
            if item in ingred_string.split():
                unit = item
                ingred_string = ingred_string.replace(item, '')

        if ',' in ingred_string:
            self.prep = ingred_string.split(',')[-1].strip()
            ingred_string = ingred_string.replace(self.prep, '')
        else:
            self.prep = None

        if not self.unit:
            self.unit = 'each'

        # at this point we are assuming that all elements have been removed
        name = ' '.join(ingred_string.split())
        self.name = name.strip(', ')


if __name__ == '__main__':
    import json
    json_list = []
    with open("ingredients.txt", "r") as file:
        for line in file:
            clean_line = line.strip()
            ingred = {}
            ingred["input"] = clean_line 
            ingred["output"] = Ingredient(clean_line).__dict__
            json_list.append(ingred)
        
    with open("ingredients.json", "w", encoding="utf-8") as f:
        json.dump(json_list, f, indent=4, ensure_ascii=False)

