# -*- coding: utf-8 -*-
"""
    pint.util
    ~~~~~~~~~

    Miscellaneous functions for pint.

    :copyright: 2016 by Pint Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""

from pyrecipe.recipe import Recipe

class RecipeOCR(Recipe):

    def __init__(self, ocr_file):
        ingredients = []
        method = []
        super().__init__()
        self._parse_file(ocr_file)
    
    def _parse_file(self, ocr_file):
        ingredients = []
        method = []
        
        with open(ocr_file) as fi:
            lines = fi.read().splitlines()
            self.recipe_name = lines.pop(0)
            lines = iter(lines)
            for line in lines:
                if line.startswith("@ingredients"):
                    line = next(lines)
                    while line != "@end":
                        ingredients.append(line)
                        line = next(lines)
                
                if line.startswith("@method"):
                    line = next(lines)
                    step = []
                    while line != "@end":
                        if line == "":
                            # remove empty strings
                            step = list(filter(None, step))
                            method.append(' '.join(step))
                            del step[:]
                        step.append(line)
                        try: 
                            line = next(lines)
                        except StopIteration:
                            del step[-1]
                            method.append(' '.join(step))
                            break
        
        self.ingredients = ingredients
        self.method = method


if __name__ == "__main__":
    recipe = RecipeOCR("output.txt")

    #recipe = Recipe('pesto')
    print(recipe)
