# -*- coding: utf-8 -*-
"""
    pyrecipe
    ~~~~~~~~

    Pyrecipe is a python application that lets you manage recipes.

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""

import os

from pint import UnitRegistry
import inflect
import ruamel.yaml as yaml

import pyrecipe.utils
from .config import __version__, __scriptname__

ureg = UnitRegistry()
ureg.load_definitions(os.path.expanduser('~/.local/lib/python3.6/site-packages/pyrecipe/culinary_units.txt'))

Q_ = ureg.Quantity

# ruamel aliases because i prefer ruamel features with pyyaml syntax
yaml_load = yaml.round_trip_load
yaml_dump = yaml.round_trip_dump


# Inflects default behaviour for return the singular of words is
# not very useful to this project because it returns false if
# it comes across a non-noun word. Therfore, the following is a
# functional work-a-round
class InflectEngine(inflect.engine):

    def __init__(self):
        super().__init__()

    def singular_noun(self, word):
        singular = super().singular_noun(word)
        if singular:
            return singular
        else:
            return word

p = InflectEngine()


