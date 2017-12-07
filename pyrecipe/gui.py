"""i
"""
from tkinter import *
from .config import *
from .recipe import Recipe


class MainGUI(Tk):
	

	def __init__(self, *args, **kwargs):
		Tk.__init__(self, *args, **kwargs)
		self.title('Pyrecipe - The python recipe management program')
		recipe_listbox = Listbox(self, height=100, width=30, selectmode=SINGLE, font=('ubuntu', 13))
		scrollb = Scrollbar(self, command=recipe_listbox.yview)
		scrollb.pack(side=RIGHT, fill=Y)
		recipe_listbox.configure(yscrollcommand=scrollb.set)
		recipe_listbox.pack(side=LEFT)

		for item in sorted(RECIPE_NAMES):
			recipe_listbox.insert(END, item)
		recipe_listbox.bind("<Double-Button-1>", self.onDoubleClk)	
		recipe = recipe_listbox.curselection()
		
		self.recipe_textbox = Text(self, height=100, width=200, font=('ubuntu', 13))
		self.recipe_textbox.pack(side=LEFT, fill=X)
	

	def onDoubleClk(self, event):
		self.recipe_textbox.delete()
		widget = event.widget
		selection=widget.curselection()
		rec_selection = widget.get(selection[0])
		r = Recipe(rec_selection)
		self.recipe_textbox.insert(END, str(r))
		

def start():
	maingui = MainGUI()
	maingui.mainloop()
