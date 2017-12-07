"""i
"""
from tkinter import *
from .config import *
from . import *
import pyrecipe.recipe as recipe


class MainGUI(Tk):
	

	def __init__(self, *args, **kwargs):
		Tk.__init__(self, *args, **kwargs)
		self.title('Pyrecipe - The python recipe management program')
		self._build_menubar()
		recipe_listbox = Listbox(self, height=50, width=30, selectmode=SINGLE, bg='white', font=('ubuntu', 13))
		scrollb = Scrollbar(self, command=recipe_listbox.yview)
		scrollb.pack(side=RIGHT, fill=Y)
		recipe_listbox.configure(yscrollcommand=scrollb.set)
		recipe_listbox.pack(side=LEFT)
		for item in sorted(RECIPE_NAMES):
			recipe_listbox.insert(END, item)
		recipe_listbox.bind("<Double-Button-1>", self.onDoubleClk)	
		recipe = recipe_listbox.curselection()
		
		self.recipe_textbox = Text(self, height=50, width=200, font=('ubuntu', 15))
		self.recipe_textbox.pack(side=LEFT, fill=X)
	

	def onDoubleClk(self, event):
		# delete text box so recipes dont keep appending inside
		self.recipe_textbox.delete('1.0', END)
		widget = event.widget
		selection=widget.curselection()
		rec_selection = widget.get(selection[0])
		r = recipe.Recipe(rec_selection)
		self._build_recipe_text(r)
	
	def _build_recipe_text(self, recipe):
		recipe_name = recipe.recipe_name
		self.recipe_textbox.insert(END, str(recipe))

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
		ver = Toplevel(self, width=100)
		ver.title("Pyrecipe Version Information")
		msg_body = recipe.version()	
		msg = Message(ver, text=msg_body)
		msg.pack()
		
		button = Button(ver, text="I am a version")
		button.pack()

	def donothing(self):
		filewin = Toplevel(self)
		button = Button(filewin, text="Do nothing button")
		button.pack()
		
def start():
	maingui = MainGUI()
	maingui.mainloop()
