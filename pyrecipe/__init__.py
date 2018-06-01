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
import inflect

import pyrecipe.config as config
import pyrecipe.db as db
from pyrecipe.spell import spell_check
from pyrecipe.recipe import *
from pyrecipe.webscraper import (RecipeWebScraper, SCRAPEABLE_SITES)

try:
    __version__ = pkg_resources.get_distribution('pyrecipe').version
except:
    __version__ = 'unknown'

__email__ = 'm.k.miller@gmx.com'
__scriptname__  = os.path.basename(sys.argv[0])

ureg = UnitRegistry()
dirr = os.path.dirname(__file__)
definitions = os.path.join(dirr, 'culinary_units.txt')
ureg.load_definitions(definitions)
p = inflect.engine()

VER_STR = """  
                 _              _              _   {0} v{1}
                (_)            | |            | |  {2}
   _ __ ___  ___ _ _ __   ___  | |_ ___   ___ | |
  | '__/ _ \/ __| | '_ \ / _ \ | __/ _ \ / _ \| |  {3} {4}
  | | |  __/ (__| | |_) |  __/ | || (_) | (_) | |  {5} {0} {6}
  |_|  \___|\___|_| .__/ \___|  \__\___/ \___/|_|
                  | |                              {7}
                  |_|                              {8}
"""

VER_STR = VER_STR.format(
    __scriptname__, __version__,
    'The recipe management program.',
    'For any questions, contact me at ', __email__,
    'or type', '--help for more info.',
    'This program may be freely redistrubuted under',
    'the terms of the GNU General Public License.'
)

def version_info():
    """Print the current version of pyrecipe and exit."""
    return VER_STR


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
