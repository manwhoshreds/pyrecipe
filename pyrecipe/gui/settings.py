#!/usr/bin/env python
"""
	add recipe class

"""

from tkinter import *
from tkinter.ttk import *
import ruamel.yaml as yaml

import pyrecipe.recipe as recipe
from pyrecipe.config import *
from pyrecipe.utils import *
from .tk_utils import *

class Settings(Toplevel):

    def __init__(self, source=''):
        Toplevel.__init__(self)
        self.geometry('800x700+150+150')
        self['takefocus'] = True
        self.title("Pyrecipe Settings")
        
        # Cancel
        self.cancel = Button(self, text='Cancel', command=self.destroy)
        self.cancel.pack(side=RIGHT)
        
