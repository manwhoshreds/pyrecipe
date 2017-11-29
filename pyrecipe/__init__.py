from pint import UnitRegistry
import os


ureg = UnitRegistry(os.path.expanduser('~/.local/lib/python3.6/site-packages/pyrecipe/culinary_units.txt'))
Q_ = ureg.Quantity




