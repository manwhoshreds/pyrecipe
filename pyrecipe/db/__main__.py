"""
    pyreicpe.db
    ~~~~~~~~~~~
    Dump the database
"""
from pyrecipe.db import get_data
import pprint

PP = pprint.PrettyPrinter()
test = get_data()
PP.pprint(test)
