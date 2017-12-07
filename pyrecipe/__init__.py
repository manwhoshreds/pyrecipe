from pint import UnitRegistry
import os
from .config import __version__, __scriptname__

__all__ = ['config', 'utils', 'recipe']


ureg = UnitRegistry()
ureg.load_definitions(os.path.expanduser('~/.local/lib/python3.6/site-packages/pyrecipe/culinary_units.txt'))
Q_ = ureg.Quantity




