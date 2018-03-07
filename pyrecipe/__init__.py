# -*- coding: utf-8 -*-
"""
    pyrecipe
    ~~~~~~~~

    Pyrecipe is a python application that lets you manage recipes.
    Recipe are saved in Yaml format.

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""

import os
import sys
import pkg_resources
from math import ceil

from pint import UnitRegistry
from ruamel.yaml import YAML
import inflect

try:
    __version__ = pkg_resources.get_distribution('pyrecipe').version
except:
    __version__ = 'unknown'

__email__ = 'm.k.miller@gmx.com'
__scriptname__  = os.path.basename(sys.argv[0])

yaml = YAML(typ='safe')
yaml.default_flow_style = False

ureg = UnitRegistry()
dirr = os.path.dirname(__file__)
definitions = os.path.join(dirr, 'culinary_units.txt')
ureg.load_definitions(definitions)


class Q_(ureg.Quantity):
    """Subclass to implement a few custom behaviors
    
    Capabilities include always rounding up to the nearest whole
    and printing plural units dependent upon the objects magnitude
    """

    def round_up(self):
        return self.__class__(ceil(self._magnitude), self._units)

    def __str__(self):
        if str(self.units) == 'each':
            return format(self)
        elif self.magnitude > 1:
            return '{} {}'.format(self.magnitude, p.plural(str(self.units)))
        else:
            return format(self)

# Inflects default behaviour for returning the singular of a word is
# not very useful to this project because it returns false if
# it comes across a non-noun word. Therfore, the following is a
# functional work-a-round
class InflectEngine(inflect.engine):
    """An inflect subclass to implement different singular behaviour"""
    def __init__(self):
        super().__init__()
        self.ignored = ['roma', 'canola', 'hummus']

    def singular_noun(self, word):
        if word in self.ignored:
            return word

        singular = super().singular_noun(word)
        if singular:
            return singular
        else:
            return word

    def plural(self, word, count=None):
        if count: 
            if count <= 1:
                return word
            else:
                word = super().plural(word)
                return word
        else:
            word = super().plural(word)
            return word

p = InflectEngine()

class Color:
    """The color class defines various colors for pyrecipe"""
    NORMAL = '\033[m'
    ERROR = '\033[1;31m'
    RECIPENAME = '\033[1;36m'
    TITLE = '\033[36m'
    NUMBER = '\033[1;33m'
    REGULAR = '\033[1;35m'
    LINE = '\033[1;37m'
    INFORM = '\033[1;36m'

color = Color()
