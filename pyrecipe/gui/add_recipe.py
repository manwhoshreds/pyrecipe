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

class AddRecipe(Toplevel):

    def __init__(self, source=''):
        Toplevel.__init__(self)
        self.geometry('800x700+150+150')
        self['takefocus'] = True
        # supplying a source turns this class into an recipe editor
        # all fields are populated with the recipe data
        self.source = source
        if self.source:
            self.title("Edit recipe")
        else:
            self.title("Add recipe")
        self.recipe = recipe.Recipe(source)
        #self._init_notebook(width=700, height=600)
        self._init_notebook()
        
        # Cancel
        self.cancel = Button(self, text='Cancel', command=self.destroy)
        self.cancel.pack(side=RIGHT)
        
        # Save 
        self.save = Button(self, text='Save', command=self.save_recipe)
        self.save.pack(side=RIGHT)
        
    def _init_notebook(self, **kw):
        self.notebook = Notebook(self)
        
        # recipe
        self.recipe_frame = Frame(self.notebook, relief=GROOVE)
        self.recipe_frame.grid(padx=5, pady=5)
        self.rn_var = StringVar(self.recipe_frame)
        self.recipe_name = Label(self.recipe_frame, text='Recipe Name')
        self.recipe_name.grid(padx=5, pady=5, row=1, column=1)
        self.rn_entry = Entry(self.recipe_frame, textvariable=self.rn_var)
        self.rn_entry.insert(0, self.recipe['recipe_name'])
        self.rn_entry.grid(padx=5, pady=5, row=1, column=2)
        self.dish_type = Label(self.recipe_frame, text='Dish Type')
        self.dish_type.grid(padx=5, pady=5, row=2, column=1)
        self.dt_var = StringVar(self)
        # workaround for tkinter optionmenus odd behaviour,
        # for a more detailed explanation, check out
        # https://stackoverflow.com/questions/19138534/tkinter-optionmenu-first-option-vanishes
        # also, another post suggest using collections deque found here
        # https://docs.python.org/3/library/collections.html#collections.deque
        prepend = ['']
        new_list = prepend + DISH_TYPES
        self.dt_var = StringVar(self)
        if self.source:
            self.dt_var.set(self.recipe['dish_type'])
        else:
            self.dt_var.set('main')
        self.dt_options = OptionMenu(self.recipe_frame, self.dt_var, *new_list)
        self.dt_options.grid(sticky="ew", row=2, column=2)
        self.prep_t_var = StringVar(self)
        
        # prep time 
        self.prep_time = Label(self.recipe_frame, text='Prep time')
        self.prep_time.grid(padx=5, pady=5, row=3, column=1)
        self.prep_time_entry = Entry(self.recipe_frame, textvariable=self.prep_t_var)
        self.prep_time_entry.insert(0, self.recipe['prep_time'])
        self.prep_time_entry.grid(padx=5, pady=5, row=3, column=2)
        
        # cook time
        self.cook_t_var = StringVar(self)
        self.cook_time = Label(self.recipe_frame, text='Cook time')
        self.cook_time.grid(padx=5, pady=5, row=4, column=1)
        self.cook_time_entry = Entry(self.recipe_frame, textvariable=self.cook_t_var)
        self.cook_time_entry.insert(0, self.recipe['cook_time'])
        self.cook_time_entry.grid(padx=5, pady=5, row=4, column=2)
       
        # ingredients	
        self.ingredients = Frame(self.notebook, **kw)
        self.ingred_var = StringVar(self.ingredients)
       
        self.ingred_label = Label(self.ingredients, text='Add ingredient: ')
        self.ingred_label.grid(padx=5, row=0, column=0)
        
        self.ingred_entry = Entry(self.ingredients, width=60, textvariable=self.ingred_var)
        self.ingred_entry.grid(padx=5, row=0, column=1)
        self.ingred_entry.bind("<Return>", self.add_ingredient)
        ToolTip(self.ingred_entry, text="This is where to enter in some ingreds")
        self.add_ingredient = Button(self.ingredients, text='add', command=self.add_ingredient)
        self.add_ingredient.grid(row=0, column=2)
       
        self.ingred_tree = Treeview(self.ingredients, height="25", selectmode='browse', columns=("A", "B", "C", "D", "E"))
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
        
        if self.source:
            if self.recipe['alt_ingredients']:
                Warn(msg="This recipe contains alt ingredient data"
                         "The pyrecipe gui is not able to handle this"
                         "feature yet. Please use the cli if you wish"
                         "to edit recipes with alt ingredients.")
            ingreds = self.recipe.get_ingredients()
            for item in ingreds:
                ingred_list = recipe.IngredientParser(item)()
                self.ingred_tree.insert('', 'end', text='test', values=(ingred_list))
        
        # method
        self.method = Frame(self.notebook, **kw)
        self.method_label = Label(self.method, text="Enter method here:")
        self.method_label.pack()
        self.method_text = Text(self.method)
        self.method_text.pack()

        if self.source:
            recipe_method = self.recipe['steps']
            method_list = []
            for item in recipe_method:
                method_list.append(item['step'])
            joined_list = ";\n".join(method_list)      
            self.method_text.insert(END, joined_list)
		
        self.notebook.add(self.recipe_frame, text='Recipe')
        self.notebook.add(self.ingredients, text='Ingredients')
        self.notebook.add(self.method, text='Method')
        self.notebook.pack()

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
        self.edit_tree_var = StringVar(self.ingred_tree)
        self.edit_tree_var.trace("w", self.change_tree_entry)
        self.tree_entry = EntryPopup(self.ingred_tree, text, textvariable=self.edit_tree_var)
        self.tree_entry.place( x=x, y=y+pady, anchor='w', width=width)
        self.tree_entry.wait_window()
        updated_ingred = self.edit_tree_var.get()
        print(updated_ingred)
    
    def add_ingredient(self, event=''):
         """
         add ingredient button

         """
         ingred_string = self.ingred_var.get()
         ingred_list = recipe.IngredientParser(ingred_string)()
         self.ingred_entry.delete(0, 'end')
         self.ingred_tree.insert('', 'end', text='test', values=(ingred_list))
    
    def change_tree_entry(self, *args, **kwargs):
        print('im running this')

    def save_recipe(self):
        recipe_data = ''
        recipe_name = self.rn_var.get()
        test_recipe_data = {}
        method = self.method_text.get("1.0", END).replace('\n', ' ').split(';')
        if not self.rn_var.get():
            Warn(msg="You must supply a recipe name")
        elif not self.dt_var.get():
            Warn(msg="You must supply a dish type")
        else:
            ingredients = []
            tree_entries = self.ingred_tree.get_children()
            for item in tree_entries:
                ingred = {}
                this_list = self.ingred_tree.item(item)['values']
                ingred['amounts'] = [{'amount': this_list[0], 'unit': this_list[2]}]
                ingred['size'] = this_list[1]
                ingred['name'] = this_list[3]
                ingred['prep'] = this_list[4]
                ingredients.append(ingred)
                    
            recipe_data += 'recipe_name: {}'.format(self.rn_var.get())
            test_recipe_data['recipe_name'] = self.rn_var.get()
            recipe_data += '\ndish_type: {}'.format(self.dt_var.get())
            test_recipe_data['dish_type'] = self.dt_var.get()

            if self.prep_t_var.get():
                recipe_data += '\nprep_time: {}'.format(self.prep_t_var.get())
                test_recipe_data['prep_time'] = self.prep_t_var.get()
            if self.cook_t_var.get():
                recipe_data += '\ncook_time: {}'.format(self.cook_t_var.get())
                test_recipe_data['cook_time'] = self.cook_t_var.get()
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
            save_data = yaml.round_trip_load(recipe_data)
            file_name = get_file_name(recipe_name)
            with open(file_name, 'w') as file: 
                yaml.round_trip_dump(save_data, file)
            self.destroy()


class EntryPopup(Entry):

    def __init__(self, parent, text, **kw):
        ''' If relwidth is set, then width is ignored '''
        super().__init__(parent, **kw)
        self.insert(0, text) 
        self['exportselection'] = False
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

if __name__ == '__main__':
   AddRecipe()
