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
from ruamel.yaml import YAML

import pyrecipe.utils
from .config import __version__, __scriptname__

ureg = UnitRegistry()
ureg.load_definitions(os.path.expanduser('~/.local/lib/python3.6/site-packages/pyrecipe/culinary_units.txt'))

Q_ = ureg.Quantity

# ruamel aliases because i prefer ruamel features with pyyaml syntax
yaml = YAML()




