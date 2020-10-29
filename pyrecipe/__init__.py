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
from math import ceil
import pkg_resources

from pint import UnitRegistry
import inflect


__version__ = pkg_resources.get_distribution('pyrecipe').version
__email__ = 'm.k.miller@gmx.com'
__scriptname__ = os.path.basename(sys.argv[0])

p = inflect.engine()

class Ureg(UnitRegistry):
    """Unit Registry subclass to add functionality"""

    def get_culinary_units(self):
        """Returns a list of units used by pyrecipe."""
        units = dir(self.sys.pru)
        aliases = []
        for item in units:
            aliases += list(self._units[item].aliases)
            # the first alias is stored in symbol
            aliases.append(self._units[item].symbol)
        units += [p.plural(u) for u in units] + aliases
        return sorted(list(set(units)))

_dir = os.path.dirname(__file__)
_definitions = os.path.join(_dir, 'culinary_units.txt')
ureg = Ureg(_definitions)
CULINARY_UNITS = ureg.get_culinary_units()

VER_STR = r"""
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
    'The python recipe management program.',
    'For any questions, contact me at', __email__,
    'or type', '--help for more information.',
    'This program may be freely redistrubuted under',
    'the terms of the GNU General Public License.'
)


class Quant(ureg.Quantity):
    """Subclass to implement a few custom behaviors

    Capabilities include always rounding up to the nearest whole
    and printing plural units dependent upon the objects magnitude
    """
    def round_up(self):
        """Round up functionality"""
        return self.__class__(ceil(self._magnitude), self._units)

    def reduce(self):
        """Reduce the quantity."""
        dim = self.dimensionality
        if "length" in str(dim):
            units = ['teaspoon', 'tablespoon', 'cup', 'pint', 'quart', 'gallon']
        elif "mass" in str(dim):
            units = ['gram', 'ounce', 'pound']
        else:
            return

        quants = {}
        for item in units:
            test = self.to(item)
            quants[test.magnitude] = str(test.units)
        reduced = min(quants, key=lambda x:abs(x-1))
        self.ito(quants[reduced])

    def __str__(self):
        if str(self.units) == 'each':
            return format(self)
        if self.magnitude > 1:
            return '{} {}'.format(self.magnitude, p.plural(str(self.units)))
        return format(self)
