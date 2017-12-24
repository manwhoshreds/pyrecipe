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

from .config import __version__, __scriptname__

ureg = UnitRegistry()
ureg.load_definitions(os.path.expanduser('~/.local/lib/python3.6/site-packages/pyrecipe/culinary_units.txt'))

Q_ = ureg.Quantity

p = inflect.engine()

# ruamel aliases because i prefer ruamel features with pyyaml syntax
yaml_load = yaml.round_trip_load
yaml_dump = yaml.round_trip_dump




