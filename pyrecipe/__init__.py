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

from pint import UnitRegistry
from ruamel.yaml import YAML
import inflect

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
