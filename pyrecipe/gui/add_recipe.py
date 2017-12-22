#!/usr/bin/env python
"""
	add recipe class

"""

from tkinter import *
from tkinter.ttk import *

from pyrecipe.config import *
from .tk_utils import *


class AddRecipe(Toplevel):

    def __init__(self):
        Toplevel.__init__(self)
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
        
        # workaround for tkinter optionmenus odd behaviour,
        # for a more detailed explanation, check out
        # https://stackoverflow.com/questions/19138534/tkinter-optionmenu-first-option-vanishes
        # also, another post suggest using collections deque found here
        # https://docs.python.org/3/library/collections.html#collections.deque
        prepend = ['']
        new_list = prepend + DISH_TYPES
        dt_options = OptionMenu(recipe, self.dt_var, *new_list)
        dt_options.grid(sticky="ew", row=2, column=2)
        self.prep_t_var = StringVar(self)
        prep_time = Label(recipe, text='Prep time')
        prep_time.grid(padx=5, pady=5, row=3, column=1)
        prep_time_entry = Entry(recipe, textvariable=self.prep_t_var)
        prep_time_entry.grid(padx=5, pady=5, row=3, column=2)
        self.cook_t_var = StringVar(self)
        cook_time = Label(recipe, text='Cook time')
        cook_time.grid(padx=5, pady=5, row=4, column=1)
        cook_time_entry = Entry(recipe, textvariable=self.cook_t_var)
        cook_time_entry.grid(padx=5, pady=5, row=4, column=2)
        
        # ingredients	
        ingredients = Frame(notebook, **kw)
        self.ingred_var = StringVar(ingredients)
        
        ingred_label = Label(ingredients, text='Add ingredient: ')
        ingred_label.grid(padx=5, row=0, column=0)
        self.ingred_entry = Entry(ingredients, width=60, textvariable=self.ingred_var)
        self.ingred_entry.grid(padx=5, row=0, column=1)
        self.ingred_entry.bind("<Return>", self.add_ingredient)
        ToolTip(self.ingred_entry, text="This is where to enter in some ingreds")
        add_ingredient = Button(ingredients, text='add', command=self.add_ingredient)
        add_ingredient.grid(row=0, column=2)
        
        self.ingred_tree = Treeview(ingredients, height="25", selectmode='browse', columns=("A", "B", "C", "D", "E"))
        self.ingred_tree.bind("<Double-Button-1>", self.edit_tree)	
        self.ingred_tree['show'] = 'headings'
        self.ingred_tree.heading("A", text='Amount')
        self.ingred_tree.column("A", minwidth=0, width=60, stretch=False)
        self.ingred_tree.heading("B", text='Size')
        self.ingred_tree.column("B", minwidth=0, width=60, stretch=NO)
        self.ingred_tree.heading("C", text='Unit')
        self.ingred_tree.column("C", minwidth=0, width=120, stretch=NO)
        self.ingred_tree.heading("D", text='Ingredients')
        self.ingred_tree.column("D", minwidth=0, width=350, stretch=NO)
        self.ingred_tree.heading("E", text='Prep')
        self.ingred_tree.column("E", minwidth=0, width=150, stretch=NO)
        self.ingred_tree.grid(padx=5, row=1, column=0, columnspan=3)

        # method
        method = Frame(notebook, **kw)
        method_label = Label(method, text="Enter method here:")
        method_label.pack()
        self.method_text = Text(method)
        self.method_text.pack()
		
        
        notebook.add(recipe, text='Recipe')
        notebook.add(ingredients, text='Ingredients')
        notebook.add(method, text='Method')
        notebook.pack()

    def edit_tree(self, event):
        ''' Executed, when a row is double-clicked. Opens
        read-only EntryPopup above the item's column, so it is possible
        to select text '''


        # what row and column was clicked on
        rowid = self.ingred_tree.identify_row(event.y)
        column = self.ingred_tree.identify_column(event.x)

        # get column position info
        x,y,width,height = self.ingred_tree.bbox(rowid, column)

        # y-axis offset
        pady = height // 2
        
        # place Entry popup properly
        text = self.ingred_tree.item(rowid, 'text')
        self.tree_entry = EntryPopup(self.ingred_tree, text)
        self.tree_entry.place( x=x, y=y+pady, anchor='w', width=width)
        print(self.tree_entry)
	
    def save_recipe(self):
        recipe_data = ''
        method = self.method_text.get("1.0", END).replace('\n', ' ').split(';')
        if not self.rn_var.get():
            Warn(msg="You must supply a recipe name")
        elif not self.dt_var.get():
            Warn(msg="You must supply a dish type")
        else:
            ingredients = []
            tree_entries = self.ingred_tree.get_children()
            for each in tree_entries:
                ingred = {}
                this_list = self.ingred_tree.item(each)['values']
                ingred['amounts'] = [{'amount': this_list[0], 'unit': this_list[2]}]
                ingred['size'] = this_list[1]
                ingred['name'] = this_list[3]
                ingred['prep'] = this_list[4]
                ingredients.append(ingred)
                    
                recipe_data += 'recipe_name: {}'.format(self.rn_var.get())
                recipe_data += '\ndish_type: {}'.format(self.dt_var.get())
                if self.prep_t_var.get():
                    recipe_data += '\nprep_time: {}'.format(self.prep_t_var.get())
                if self.cook_t_var.get():
                    recipe_data += '\ncook_time: {}'.format(self.cook_t_var.get())
                recipe_data += '\ningredients:'
                for item in ingredients:
                    recipe_data += '\n  - name: {}'.format(item['name'])
                    recipe_data += '\n    amounts:'
                    recipe_data += '\n      - amount: {}'.format(item['amounts'][0]['amount'])
                    recipe_data += '\n        unit: {}'.format(item['amounts'][0]['unit'])
                    if item['size']:
                        recipe_data += '\n    size: {}'.format(item['size'])
                    if item['prep']:
                        recipe_data += '\n    prep: {}'.format(item['prep'])
                
                recipe_data += "\nsteps:"
                for item in method:
                    recipe_data += "\n  - step: {}".format(item)
                
                recipe_data += VIM_MODE_LINE
                #TESTING	
                test = yaml.load(recipe_data)
                PP.pprint(test)
                self.destroy()

    def add_ingredient(self, event=''):
        """
        add ingredient button

        """
        ingred_string = self.ingred_var.get()
        ingred_list = ingred_str_to_list(ingred_string)
        self.ingred_entry.delete(0, 'end')
        self.ingred_tree.insert('', 'end', text='test', values=(ingred_list))

def ingred_str_to_list(string):
    """given an ingredient as a string, we simply
    return as alist
    """
    amount = ''
    size = ''
    unit = ''
    name = ''
    prep = ''
    raw_list = string.split()	
    ingred_list = [x.lower() for x in raw_list]
    for item in ingred_list:
        if re.search(r'\d+', item):
            amount = item
            ingred_list.remove(item)
            break
    for item in SIZE_STRINGS:
        if item in ingred_list:
            size = item
            ingred_list.remove(item)
    for item in INGRED_UNITS:	
        if item in ingred_list:
            unit = item
            ingred_list.remove(item)
    for item in PREP_TYPES:
        if item in ingred_list:
            prep = item
            ingred_list.remove(item)
    
    if not unit:
        unit = 'each'
    
    name = ' '.join(ingred_list)
    return [amount, size, unit, name, prep]

class EntryPopup(Entry):

    def __init__(self, parent, text, **kw):
        ''' If relwidth is set, then width is ignored '''
        super().__init__(parent, **kw)
        self.insert(0, text) 
        self.var = StringVar(self)
        self['exportselection'] = False
        self['textvariable'] = self.var
        self.focus_force()
        self.bind("<Control-a>", self.selectAll)
        self.bind("<Escape>", lambda *ignore: self.destroy())
        self.bind("<Return>", self.enter)

    def selectAll(self, *ignore):
        ''' Set selection on the whole text '''
        self.selection_range(0, 'end')

        # returns 'break' to interrupt default key-bindings
        return 'break'

    def enter(self, event):
        self.destroy()
        print(self.var.get())
        return self.var.get()

if __name__ == '__main__':
   AddRecipe()
