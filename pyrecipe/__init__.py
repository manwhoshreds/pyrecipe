from pint import UnitRegistry
import os

__all__ = ['config', 'utils', 'recipe']

#ureg = UnitRegistry(os.path.expanduser('~/.local/lib/python3.6/site-packages/pyrecipe/culinary_units.txt'))
ureg = UnitRegistry()
Q_ = ureg.Quantity




