"""
    pyreicpe.db
    ~~~~~~~~~~~
    
    The main database file for pyrecipe.
"""
from pyrecipe.db import get_data
import pprint

PP = pprint.PrettyPrinter()
test = get_data()
PP.pprint(test)
