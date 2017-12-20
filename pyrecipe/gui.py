"""i
"""

import re
import os

from tkinter import *
from tkinter.ttk import *
from .config import *
from . import *
from numbers import Number


import pyrecipe.recipe as recipe



class MainGUI(Tk):
	

	def __init__(self, *args, **kwargs):
		Tk.__init__(self, *args, **kwargs)
		self.title('Pyrecipe - The python recipe management program')
		self._build_menubar()

		self.top_bar = Frame()
		self.top_bar.pack(fill=X)
		new_recipe = Button(self.top_bar, text="New", command=AddRecipe)
		new_recipe.pack(side=LEFT)
		
		self.left_pane = Frame()
		self.left_pane.pack(side=LEFT)
		
		recipe_listbox = Listbox(self.left_pane, height=50, width=30, selectmode=SINGLE, bg='white', font=('ubuntu', 13))

		entry = AutoEntry(RECIPE_NAMES, self.left_pane)
		entry.pack(side=TOP, fill=X)
		scrollb = Scrollbar(self.left_pane, command=recipe_listbox.yview)
		scrollb.pack(side=RIGHT, fill=Y)
		recipe_listbox.configure(yscrollcommand=scrollb.set)
		recipe_listbox.pack(side=LEFT)
		for item in sorted(RECIPE_NAMES):
			recipe_listbox.insert(END, item)
		recipe_listbox.bind("<Double-Button-1>", self.onDoubleClk)	
		recipe_listbox.bind("<Button-3>", self.onRightClk)
		recipe = recipe_listbox.curselection()
		
		self.recipe_textbox = Text(self, height=50, width=200, font=('ubuntu', 16))
		self.recipe_textbox.pack(side=LEFT, fill=X)
	
	def onRightClk(self, event):
		Warn(msg="yup its working")
	
	def onDoubleClk(self, event):
		# State Normal on click on disabled when we finish building text
		# this is nescassary to for text to be read-only
		self.recipe_textbox.config(state=NORMAL)
		# delete text box so recipes dont keep appending inside
		self.recipe_textbox.delete('1.0', END)
		widget = event.widget
		selection = widget.curselection()
		rec_selection = widget.get(selection[0])
		r = recipe.Recipe(rec_selection)
		self._build_recipe_text(r)
	
	def _build_recipe_text(self, recipe):
		recipe_name = recipe.recipe_name
		self.recipe_textbox.insert(END, str(recipe))
		self.recipe_textbox.config(state=DISABLED)

	def _build_menubar(self):
		# filemenu
		menubar = Menu(self)
		filemenu = Menu(menubar, tearoff=0)
		filemenu.add_command(label="New", command=self.donothing)
		filemenu.add_command(label="Open", command=self.donothing)
		filemenu.add_command(label="Save", command=self.donothing)
		filemenu.add_command(label="Save as...", command=self.donothing)
		filemenu.add_command(label="Close", command=self.donothing)

		filemenu.add_separator()

		filemenu.add_command(label="Exit", command=self.quit)
		menubar.add_cascade(label="File", menu=filemenu)
		
		# editmenu	
		editmenu = Menu(menubar, tearoff=0)
		editmenu.add_command(label="Undo", command=self.donothing)

		editmenu.add_separator()

		editmenu.add_command(label="Cut", command=self.donothing)
		editmenu.add_command(label="Copy", command=self.donothing)
		editmenu.add_command(label="Paste", command=self.donothing)
		editmenu.add_command(label="Delete", command=self.donothing)
		editmenu.add_command(label="Select All", command=self.donothing)
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

	def donothing():
		pass



class AutoEntry(Entry):
    
	
    def __init__(self, somelist, *args, **kwargs):
        Entry.__init__(self, *args, **kwargs)
        self.somelist = somelist       
        self.var = self["textvariable"]
        if self.var == '':
            self.var = self["textvariable"] = StringVar()

        self.var.trace('w', self.changed)
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
                    recipe_listbox.insert(END, w)
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

class AddRecipe(Toplevel):

	
	def __init__(self):
		Toplevel.__init__(self)
		self.ingredients = {}
		self.geometry('800x700+150+150')
		self.title("Add a recipe")
		self._init_notebook(width=700, height=600)
		cancel = Button(self, text='Cancel', command=self.destroy)
		cancel.pack(side=RIGHT)
		save = Button(self, text='Save', command=self.save_recipe)
		save.pack(side=RIGHT)
		
	def _init_notebook(self, **kw):
		notebook = Notebook(self)
		
		# recipe
		recipe = Frame(notebook, relief=GROOVE)
		recipe.grid(padx=5, pady=5)
		self.rn_var = StringVar(recipe)
		recipe_name = Label(recipe, text='Recipe Name')
		recipe_name.grid(padx=5, pady=5, row=1, column=1)
		rn_entry = Entry(recipe, textvariable=self.rn_var)
		rn_entry.grid(padx=5, pady=5, row=1, column=2)
		dish_type = Label(recipe, text='Dish Type')
		dish_type.grid(padx=5, pady=5, row=2, column=1)
		self.dt_var = StringVar(self)
		self.dt_var.set('dish')
		dt_options = OptionMenu(recipe, self.dt_var, *DISH_TYPES)
		dt_options.grid(row=2, column=2)
		
		# ingredients	
		ingredients = Frame(notebook, **kw)
		self.ingred_var = StringVar(ingredients)
		
		ingred_label = Label(ingredients, text='Add ingredient: ')
		ingred_label.grid(padx=5, row=0, column=0)
		self.ingred_entry = Entry(ingredients, width=60, textvariable=self.ingred_var)
		self.ingred_entry.grid(padx=5, row=0, column=1)
		add_ingredient = Button(ingredients, text='add', command=self.add_ingredient)
		add_ingredient.grid(row=0, column=2)
		
		self.tree = Treeview(ingredients, height="25", columns=("A", "B", "C", "D"))
		self.tree['show'] = 'headings'
		self.tree.heading("A", text='Amount')
		self.tree.column("A", minwidth=0, width=120, stretch=NO)
		self.tree.heading("B", text='Unit')
		self.tree.column("B", minwidth=0, width=120, stretch=NO)
		self.tree.heading("C", text='Ingredients')
		self.tree.column("C", minwidth=0, width=350, stretch=NO)
		self.tree.heading("D", text='Prep')
		self.tree.column("D", minwidth=0, width=150, stretch=NO)
		self.tree.grid(padx=5, row=1, column=0, columnspan=3)

		# method
		method = Frame(notebook, **kw)
		
		
		notebook.add(recipe, text='Recipe')
		notebook.add(ingredients, text='Ingredients')
		notebook.add(method, text='Method')
		notebook.pack()
	
	def save_recipe(self):
		recipe_data = ''
		if not self.rn_var.get():
			Warn(msg="You must supply a recipe name")
		elif not self.dt_var.get():
			Warn(msg="You must supply a dish type")
		else:
			recipe_data += 'recipe_name: {}'.format(self.rn_var.get())
			recipe_data += '\ndish_type: {}'.format(self.dt_var.get())
			recipe_data += '\ningredients:'
			for item in self.ingredients:
				recipe_data += '\n  - name: {}'.format(item['name'])
				recipe_data += '\n    amounts:'
				recipe_data += '\n      - amount: {}'.format(item['amounts'][0]['amount'])
				recipe_data += '\n        unit: {}'.format(item['amounts'][0]['unit'])
				if item['prep']:
					pass
			test = yaml.load(recipe_data)
			PP.pprint(test)
			self.destroy()

	def add_ingredient(self):
		ingred_string = self.ingred_var.get()
		ingred_list = convert_ingred_string_to_list(ingred_string)
		self.ingred_entry.delete(0, 'end')
		self.tree.insert('', 'end', text='test', values=(ingred_list))

def convert_ingred_string_to_list(string):
	amount = ''
	unit = ''
	name = ''
	prep = ''
	ingred_list = string.split()	
	print(ingred_list[0])
	if isinstance(ingred_list[0], Number):
		amount = ingred_list[0]
	if 'tablespoon' in ingred_list:
		unit = 'tablespoon'
	return [amount, unit, name, prep]


class Warn(Toplevel):
	
	def __init__(self, msg):
		Toplevel.__init__(self)
		self.title("Pyrecipe Information")
		self.geometry('200x100+800+450')

		message = Message(self, text=msg, width=200)
		message.pack()
		
		button = Button(self, text="Ok", command=self.destroy)
		button.pack(side=BOTTOM)
		self.play_sound()

	def play_sound(self):
		self.sound()
		
	def sound(self):
		os.system('play -q /usr/share/sounds/KDE-Sys-Warning.ogg')
		

class ToolTip(object):
	'''
		create a tooltip for a given widget
	'''
	def __init__(self, widget, text='widget info'):
		self.widget = widget
		self.text = " {} ".format(text)
		self.widget.bind("<Enter>", self.enter)
		self.widget.bind("<Leave>", self.close)

	def enter(self, event=None):
		x = y = 0
		x, y, cx, cy = self.widget.bbox("insert")
		x += self.widget.winfo_rootx() + 25
		y += self.widget.winfo_rooty() + 20
		# creates a toplevel window
		self.tw = Toplevel(self.widget)
		# Leaves only the label and removes the app window
		self.tw.wm_overrideredirect(True)
		self.tw.wm_geometry("+%d+%d" % (x, y))
		label = Label(self.tw, text=self.text, justify='left',
				background='yellow', relief='solid', borderwidth=1,
				font=("unbuntu", "12", "normal"))
		label.pack(ipadx=1)

	def close(self, event=None):
		if self.tw:
			self.tw.destroy()

def start():
	maingui = MainGUI()
	maingui.mainloop()
