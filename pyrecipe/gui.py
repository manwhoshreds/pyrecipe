"""i
"""

import re
import os

from tkinter import *
from tkinter.ttk import *
from .config import *
from . import *

import pyrecipe.recipe as recipe



class MainGUI(Tk):
	

	def __init__(self, *args, **kwargs):
		Tk.__init__(self, *args, **kwargs)
		self.fleft = Frame()
		self.fleft.pack(side=LEFT)
		self.title('Pyrecipe - The python recipe management program')
		new_recipe = Button(self.fleft, text="New", command=AddRecipe)
		new_recipe.pack()
		self._build_menubar()
		recipe_listbox = Listbox(self.fleft, height=50, width=30, selectmode=SINGLE, bg='white', font=('ubuntu', 13))
		entry = AutoEntry(RECIPE_NAMES, self.fleft, width=30)
		entry.pack(side=TOP, fill=Y)
		scrollb = Scrollbar(self.fleft, command=recipe_listbox.yview)
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

	ingredients = []
	
	def __init__(self):
		Toplevel.__init__(self)
		self.geometry('700x700+200+200')
		self.title("Add a recipe")
		self._init_notebook(width=690, height=600)
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
		self.amount_var = StringVar(ingredients)
		self.unit_var = StringVar(ingredients)
		self.prep_var = StringVar(ingredients)
		

		ingred_label = Label(ingredients, text='Add ingredient: ')
		ingred_label.grid(padx=3, row=0, column=0)
		self.ingred_entry = Entry(ingredients, width=60, textvariable=self.ingred_var)
		self.ingred_entry.grid(padx=3, row=0, column=1)
		#amount_label = Label(ingredients, text='Amount')
		#amount_label.grid(row=2, column=0)
		#self.amount_entry = Entry(ingredients, textvariable=self.amount_var)
		#self.amount_entry.grid(row=3, column=0)
		#unit_label = Label(ingredients, text='Unit')
		#unit_label.grid(row=4, column=0)
		#self.unit_entry = Entry(ingredients, textvariable=self.unit_var)
		#self.unit_entry.grid(row=5, column=0)
		#prep_label = Label(ingredients, text='Preparation')
		#prep_label.grid(row=6, column=0)
		#self.prep_entry = Entry(ingredients, textvariable=self.prep_var)
		#self.prep_entry.grid(row=7, column=0)
		#prep_tooltip = ToolTip(self.prep_entry, "this is just a tip")
		add_ingredient = Button(ingredients, text='add', command=self.add_ingredient)
		add_ingredient.grid(row=0, column=2)
		
		tree = Treeview(ingredients, columns=("A", "B", "C", "D"))
		tree['show'] = 'headings'
		tree.heading("A", text='Amount')
		tree.column("A", minwidth=0, width=100, stretch=NO)
		tree.heading("B", text='Unit')
		tree.column("B", minwidth=0, width=100, stretch=NO)
		tree.heading("C", text='Ingredients')
		tree.column("C", minwidth=0, width=300, stretch=NO)
		tree.heading("D", text='Prep')
		tree.column("D", minwidth=0, width=100, stretch=NO)
		tree.grid(row=1, column=0, columnspan=3)

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
			for item in AddRecipe.ingredients:
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
		if not self.ingred_var.get():
			Warn(msg="You must supply an Ingredient")
		elif not self.unit_var.get():
			Warn(msg="You must supply a unit")
		else:
			ingred_string = "{} {} {} {}\n".format(self.amount_var.get(),
												 self.unit_var.get(),
												 self.ingred_var.get(),
												 self.prep_var.get()
												)
			
			ingred = {}
			ingred['name'] = self.ingred_var.get()
			ingred['amounts'] = [{'amount': self.amount_var.get(), 'unit': self.unit_var.get()}]
			if self.prep_var.get():
				ingred['prep'] = self.prep_var.get()


			AddRecipe.ingredients.append(ingred)
			print(AddRecipe.ingredients)
			
			self.ingred_entry.delete(0, 'end')
			self.amount_entry.delete(0, 'end')
			self.unit_entry.delete(0, 'end')
			self.prep_entry.delete(0, 'end')
			self.ingredient_textbox.insert(END, ingred_string)


class Warn(Toplevel):
	
	def __init__(self, msg):
		Toplevel.__init__(self)
		self.title("Pyrecipe Information")
		self.geometry('200x100+800+450')

		message = Message(self, text=msg, width=200)
		message.pack()
		
		button = Button(self, text="Ok", command=self.destroy)
		button.pack(side=BOTTOM)
		#self.sound()
		
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
