"""gui
"""
import re
import os
import time

from tkinter import *
from tkinter.ttk import *
from numbers import Number

import pyrecipe.recipe as recipe
from pyrecipe.gui.add_recipe import AddRecipe
from pyrecipe.gui.settings import Settings
from pyrecipe.gui.tk_utils import *
import pyrecipe.config as conf
#from .config import *
from pyrecipe.utils import *




class MainGUI(Tk):
	
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title('Pyrecipe - The python recipe management program')
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self._build_menubar()
        self.top_bar = Frame()
        self.top_bar.pack(fill=X)
        new_recipe = Button(self.top_bar, text="New", command=self.add_recipe)
        new_recipe.pack(side=LEFT)
        self.edit_recipe = Button(self.top_bar, text="Edit", command=self.edit_recipe)
        self.edit_recipe.pack(side=LEFT)

        
        self.left_pane = Frame()
        self.left_pane.pack(side=LEFT)
        search = Label(self.left_pane, text="Search Recipes")
        search.pack()
        entry = AutoEntry(conf.RECIPE_NAMES, self.left_pane)
        entry.pack(fill=X)
        self.recipe_listbox = Listbox(self.left_pane, height=50, width=30, selectmode=SINGLE, bg='white', font=('ubuntu', 13))
        scrollb = Scrollbar(self.left_pane, command=self.recipe_listbox.yview)
        scrollb.pack(side=RIGHT, fill=Y)
        self.recipe_listbox.configure(yscrollcommand=scrollb.set)
        self.recipe_listbox.pack(side=LEFT)
        self.refresh_recipes()
        self.recipe_listbox.bind("<Double-Button-1>", self.onDoubleClk)	
        self.recipe_listbox.bind("<Button-1>", self.onLeftClk)
        self.recipe_listbox.bind("<Button-3>", self.onRightClk)
        self.selection = self.recipe_listbox.curselection()
        
        # listbox context menu
        self.popup_menu = Menu(self.recipe_listbox, tearoff=0)
        self.popup_menu.add_command(label="Edit", command=self.edit_recipe)
        self.popup_menu.add_command(label="Select All", command=self.donothing)
        
        self.recipe_textbox = Text(self, height=50, width=100, font=('ubuntu', 16))
        self.recipe_textbox.pack(side=LEFT, fill=X)

        self.right_pane = Frame()
        self.right_pane.pack(side=RIGHT, fill=BOTH)
        test = Button(self.right_pane, width=50, text="test", command=self.donothing)
        test.pack()
    
    def onLeftClk(self, event):
        self.popup_menu.unpost()

    def _get_selection(self):
        try:
            self.recipe = self.recipe_listbox.curselection()
            rec_selection = self.recipe_listbox.get(self.recipe[0])
            return rec_selection
        except IndexError:
            pass

    def refresh_recipes(self):
        self.recipe_listbox.delete(0, END)
        for item in sorted(conf.RECIPE_NAMES):
            self.recipe_listbox.insert(END, item)

    def add_recipe(self):
        recipe_add = AddRecipe()
        recipe_add.wait_window()
        self.refresh_recipes()

    def edit_recipe(self):
        rec_selection = self._get_selection()
        if not rec_selection:
            Warn(msg="Select a recipe from the list box")
        else:
            r = recipe.Recipe(rec_selection)
            if r['alt_ingredients']:
                warning = Warn(msg="This recipe contains alt ingredient data "
                                   "The pyrecipe gui is not able to handle this "
                                   "feature yet. Please use the cli if you wish "
                                   "to edit recipes with alt ingredients.")
                warning.wait_window()
            else:
                AddRecipe(rec_selection)

        
    def onRightClk(self, event):
        self.popup_menu.unpost()
        self.recipe_listbox.select_clear(0, END)
        y = event.y_root - 120
        index = self.recipe_listbox.nearest(y)
        self.recipe_listbox.select_set(index)
        self.popup_menu.post(event.x_root, event.y_root)
        self._get_selection()
    
    def onDoubleClk(self, event):
        # State Normal on click on disabled when we finish building text
        # this is nescassary for text to be read-only
        self.recipe_textbox.config(state=NORMAL)
        # delete text box so recipes dont keep appending inside
        self.recipe_textbox.delete('1.0', END)
        widget = event.widget
        selection = widget.curselection()
        recipe_selection = widget.get(selection[0])
        r = recipe.Recipe(recipe_selection)
        self._build_recipe_text(r)
    
    def _build_recipe_text(self, recipe):
        recipe_name = recipe.recipe_name
        test = len(recipe_name)
        #self.recipe_textbox.insert(END, recipe_name)
        #self.recipe_textbox.tag_add("recipe_name", "1.0", "1."+str(test))
        #self.recipe_textbox.tag_config("recipe_name", background="yellow", foreground="blue")
        
        self.recipe_textbox.insert(END, str(recipe))
        self.recipe_textbox.config(state=DISABLED)

    def _build_menubar(self):
        # filemenu
        menubar = Menu(self)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.add_recipe)
        filemenu.add_command(label="Open", command=self.donothing)
        filemenu.add_command(label="Close", command=self.donothing)

        filemenu.add_separator()

        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        # editmenu	
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Settings", command=Settings)
        menubar.add_cascade(label="Edit", menu=editmenu)
        
        # helpmenu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About...", command=self.show_version)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.config(menu=menubar)

    def show_version(self):
        ver = Toplevel(width=800, height=800)
        ver.title("Pyrecipe Version Information")

        verframe = Frame(ver, width=800, height=800)
        verframe.pack()
        
        msg_body = recipe.version(text_only=True)	
        msg = Message(verframe, text=msg_body)
        msg.pack()
        
        button = Button(ver, text="Ok", command=ver.destroy)
        button.pack()

    def donothing(self):
        pass


class AutoEntry(Entry):

    
    def __init__(self, somelist, *args, **kwargs):
        Entry.__init__(self, *args, **kwargs)
        self.somelist = somelist       
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = StringVar()
        self.var.trace('w', self.changed)
        self.bind("<Return>", self.selection)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)
        self.lb_up = False

    def changed(self, name, index, mode):  

        if self.var.get() == '':
            self.lb.destroy()
            self.lb_up = False
        else:
            words = self.comparison()
            if words:            
                if not self.lb_up:
                    self.lb = Listbox()
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    self.lb.place(x=self.winfo_x(), y=self.winfo_y()+self.winfo_height())
                    self.lb_up = True
                
                self.lb.delete(0, END)
                for w in words:
                    self.lb.insert(END,w)
                    #recipe_listbox.insert(END, w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False
        
    def selection(self, event):

        if self.lb_up:
            self.var.set(self.lb.get(ACTIVE))
            self.lb.destroy()
            self.lb_up = False
            self.icursor(END)

    def up(self, event):

        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != '0':                
                self.lb.selection_clear(first=index)
                index = str(int(index)-1)                
                self.lb.selection_set(first=index)
                self.lb.activate(index) 

    def down(self, event):

        if self.lb_up:
            if self.lb.curselection() == ():
                index = '0'
            else:
                index = self.lb.curselection()[0]
            if index != END:                        
                self.lb.selection_clear(first=index)
                index = str(int(index)+1)        
                self.lb.selection_set(first=index)
                self.lb.activate(index) 

    def comparison(self):
        pattern = re.compile('.*' + self.var.get() + '.*')
        return [w for w in self.somelist if re.match(pattern, w)]

def start():
    maingui = MainGUI()
    maingui.mainloop()
