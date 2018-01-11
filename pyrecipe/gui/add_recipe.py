#!/usr/bin/env python
"""
    The add_recipe module include classes to 
    add or edit a recipe

"""

import ruamel.yaml as yaml
import functools

import pyrecipe.recipe as recipe
from pyrecipe.config import *
from pyrecipe.utils import *
import pyrecipe.gui
from pyrecipe.gui.tk_utils import *

class AddRecipe(tk.Toplevel):
    """Add a recipe.
    
    The AddRecipe() class is a toplevel dialouge used to 
    add a recipe to the recipe store. If a source argument
    is passed with the class instance, a dialouge is produced
    with fields aleady populated with the relavant information.
    """
    def __init__(self, source=''):
        super().__init__()
        self['takefocus'] = True
        # supplying a source turns this class into a recipe editor
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
        self.cancel = tk.Button(self, text='Cancel', command=self.destroy)
        self.cancel.pack(side=tk.RIGHT)
        
        # Save 
        self.save = tk.Button(self, text='Save', command=self.save_recipe)
        self.save.pack(side=tk.RIGHT)
        
    def _init_notebook(self, **kw):
        self.notebook = ttk.Notebook(self)
        
        # recipe
        self.recipe_frame = tk.Frame(self.notebook)
        self.recipe_frame.grid(padx=5, pady=5)
        self.rn_var = tk.StringVar(self.recipe_frame)
        self.recipe_name = tk.Label(self.recipe_frame, text='Recipe Name:')
        self.recipe_name.grid(padx=5, pady=5, row=1, column=1)
        self.rn_entry = tk.Entry(self.recipe_frame, textvariable=self.rn_var)
        self.rn_entry.insert(0, self.recipe['recipe_name'])
        self.rn_entry.grid(padx=5, pady=5, row=1, column=2)
        self.dish_type = tk.Label(self.recipe_frame, text='Dish Type:')
        self.dish_type.grid(padx=5, pady=5, row=2, column=1)
        self.dt_var = tk.StringVar(self)
        self.dt_var = tk.StringVar(self)
        if self.source:
            self.dt_var.set(self.recipe['dish_type'])
        else:
            self.dt_var.set('main')
        self.dt_options = ttk.Combobox(self.recipe_frame, values=DISH_TYPES, textvariable=self.dt_var)
        self.dt_options.grid(sticky="ew", row=2, column=2)
        self.prep_t_var = tk.StringVar(self)
        
        # prep time 
        self.prep_time = tk.Label(self.recipe_frame, text='Prep time:')
        self.prep_time.grid(padx=5, pady=5, row=3, column=1)
        self.prep_time_entry = tk.Entry(self.recipe_frame, textvariable=self.prep_t_var)
        self.prep_time_entry.insert(0, self.recipe['prep_time'])
        self.prep_time_entry.grid(padx=5, pady=5, row=3, column=2)
        
        # cook time
        self.cook_t_var = tk.StringVar(self)
        self.cook_time = tk.Label(self.recipe_frame, text='Cook time:')
        self.cook_time.grid(padx=5, pady=5, row=4, column=1)
        self.cook_time_entry = tk.Entry(self.recipe_frame, textvariable=self.cook_t_var)
        self.cook_time_entry.insert(0, self.recipe['cook_time'])
        self.cook_time_entry.grid(padx=5, pady=5, row=4, column=2)
       
        # ingredients	
        self.ingredients = tk.Frame(self.notebook, **kw)
        self.ingred_var = tk.StringVar(self.ingredients)
       
        self.ingred_label = tk.Label(self.ingredients, text='Add ingredient: ')
        self.ingred_label.grid(padx=5, row=0, column=0)
        
        self.ingred_entry = tk.Entry(self.ingredients, width=60, textvariable=self.ingred_var)
        self.ingred_entry.grid(padx=5, row=0, column=1)
        self.ingred_entry.bind("<Return>", self.add_ingredient)
        ToolTip(self.ingred_entry, text="This is where to enter in some ingreds")
        self.add_ingredient = tk.Button(self.ingredients, text='add', command=self.add_ingredient)
        self.add_ingredient.grid(row=0, column=2)
        
        # Treeview
        self.ingred_tree = IngredTree(self.ingredients)
        
        if self.source:
            ingreds = self.recipe.get_ingredients()
            for item in ingreds:
                ingred_list = recipe.IngredientParser(item)()
                self.ingred_tree.insert('', 'end', text='test', values=(ingred_list))
        
        # method
        self.method = tk.Frame(self.notebook, **kw)
        self.method_label = tk.Label(self.method, text="Enter method here:")
        self.method_label.pack()
        self.method_text = tk.Text(self.method)
        self.method_text.pack()
        if self.source:
            recipe_method = self.recipe['steps']
            method_list = []
            for item in recipe_method:
                method_list.append(item['step'])
            joined_list = ";\n".join(method_list)      
            self.method_text.insert(tk.END, joined_list)
	
        self.notebook.add(self.recipe_frame, text='Recipe')
        self.notebook.add(self.ingredients, text='Ingredients')
        self.notebook.add(self.method, text='Method')
        self.notebook.pack()
    
    def add_ingredient(self, event=''):
        """Add ingredient button"""
        ingred_string = self.ingred_var.get()
        if ingred_string:
            ingred_list = recipe.IngredientParser(ingred_string)()
            self.ingred_entry.delete(0, 'end')
            self.ingred_tree.insert('', 'end', text='test', values=(ingred_list))
        else:
            pass
         
    def save_recipe(self):
        """Save the recipe"""
        recipe_data = ''
        recipe_name = self.rn_var.get()
        test_recipe_data = {}
        method = self.method_text.get("1.0", tk.END).replace('\n', ' ').split(';')
        if not self.rn_var.get():
            center(Warn(msg="You must supply a recipe name"))
        elif not self.dt_var.get():
            center(Warn(msg="You must supply a dish type"))
        else:
            ingredients = []
            tree_entries = self.ingred_tree.get_children()
            if not tree_entries:
                Warn(msg="You must add at least one ingredient")
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


class IngredTree(ttk.Treeview):
    """A simple editable treeview
    
    It uses the following events from Treeview:
        <Button-1>
    
    The first is used to configure cell editors.
    The second is called after a cell was changed.
    You can know wich cell is being configured or edited, using:
        get_event_info()
    """
    def __init__(self, master=None, **kw):
        ttk.Treeview.__init__(self, master, **kw)

        self._curfocus = None
        self._inplace_widgets = {}
        self._inplace_vars = {}
        self._event_info = ()

        self['height'] = "25"
        self['selectmode'] = 'browse'
        self['show'] = 'headings'
        self['columns'] = ("A", "B", "C", "D", "E")
        self.heading("A", text='Amount')
        self.column("A", minwidth=0, width=60)
        self.heading("B", text='Size')
        self.column("B", minwidth=0, width=60)
        self.heading("C", text='Unit')
        self.column("C", minwidth=0, width=120)
        self.heading("D", text='Ingredients')
        self.column("D", minwidth=0, width=350)
        self.heading("E", text='Prep')
        self.column("E", minwidth=0, width=150)
        self.grid(padx=5, row=1, column=0, columnspan=3)
        
        self.bind('<Button-1>', self._kill_widgets)
        self.bind('<Double-Button-1>', self._edit)
    
    def _kill_widgets(self, event=None):
        try: 
            # Delete other widget every time we click on the tree
            # also updat last entry before moving on with next incase
            # the user double clicks on another cell with out pressing
            # enter on last cell
            self.tree_entry.destroy()
            self.updated_ingred = self._inplace_vars[self.cell_id].get()
            self._set_value(self.item, self.col, self.updated_ingred)
        except AttributeError:
            pass
    
    def _edit(self, event):
        """Executed, when a row is double-clicked. Opens
        EntryPopup inplace of the cell entry."""
        # position info 
        self.item = self.selection()[0]
        self.col = self.identify_column(event.x)
        self._event_info = (self.item, self.col)
        self.cell_id = self.item + self.col
        
        # get cell box values
        x,y,width,height = self.bbox(self.item, self.col)

        # y-axis offset
        pady = height // 2
        
        # get value
        cell_value = self._get_value(self.item, self.col)
        
        # place Entry popup properly
        self._inplace_vars[self.cell_id] = tk.StringVar()
        edit_tree_var = self._inplace_vars[self.cell_id]
        if self.col == '#2':
            self.tree_entry = ComboPopup(self, cell_value, values=SIZE_STRINGS, textvariable=edit_tree_var)
        elif self.col == '#3':
            self.tree_entry = ComboPopup(self, cell_value, values=INGRED_UNITS, textvariable=edit_tree_var)
        elif self.col == '#5':
            self.tree_entry = ComboPopup(self, cell_value, values=PREP_TYPES, textvariable=edit_tree_var)
            #self.tree_entry.set(cell_value)
        else:
            self.tree_entry = EntryPopup(self, cell_value, textvariable=edit_tree_var)
        
        self.tree_entry.place(x=x, y=y+pady, anchor='w', width=width)
        self.tree_entry.wait_window()
        
        self.updated_ingred = self._inplace_vars[self.cell_id].get()
        
        # set
        self._set_value(self.item, self.col, self.updated_ingred)

    
    def delete(self, *items):
        self.after_idle(self.__updateWnds)
        ttk.Treeview.delete(self, *items)

    def yview(self, *args):
        """Update inplace widgets position when doing vertical scroll"""
        self.after_idle(self.__updateWnds)
        ttk.Treeview.yview(self, *args)

    def yview_scroll(self, number, what):
        self.after_idle(self.__updateWnds)
        ttk.Treeview.yview_scroll(self, number, what)

    def yview_moveto(self, fraction):
        self.after_idle(self.__updateWnds)
        ttk.Treeview.yview_moveto(self, fraction)

    def xview(self, *args):
        """Update inplace widgets position when doing horizontal scroll"""
        self.after_idle(self.__updateWnds)
        ttk.Treeview.xview(self, *args)

    def xview_scroll(self, number, what):
        self.after_idle(self.__updateWnds)
        ttk.Treeview.xview_scroll(self, number, what)

    def xview_moveto(self, fraction):
        self.after_idle(self.__updateWnds)
        ttk.Treeview.xview_moveto(self, fraction)

    def __updateWnds(self, event=None):
        if not self._curfocus:
            return
        item = self._curfocus
        cols = self.__get_display_columns()
        for col in cols:
            if col in self._inplace_widgets:
                wnd = self._inplace_widgets[col]
                bbox = ''
                if self.exists(item):
                    bbox = self.bbox(item, column=col)
                if bbox == '':
                    wnd.place_forget()
                elif col in self._inplace_widgets_show:
                    wnd.place(x=bbox[0], y=bbox[1],
                        width=bbox[2], height=bbox[3])

    def __clear_inplace_widgets(self):
        """Remove all inplace edit widgets."""
        cols = self.__get_display_columns()
        for c in cols:
            if c in self._inplace_widgets:
                widget = self._inplace_widgets[c]
                widget.place_forget()
                self._inplace_widgets_show.pop(c, None)
                #widget.destroy()
                #del self._inplace_widgets[c]

    def _get_display_columns(self):
        cols = self.cget('displaycolumns')
        show = (str(s) for s in self.cget('show'))
        return cols

    def get_event_info(self):
        return self._event_info

    def _get_value(self, item, col):
        return self.set(item, col)

    def _set_value(self, item, col, value):
        self.set(item, col, value)
        self.__event_info = (col,item)
        self.event_generate('<<TreeviewCellEdited>>')

    def inplace_entry(self, col, item):
        if col not in self._inplace_vars:
            self._inplace_vars[col] = tk.StringVar()
        svar = self._inplace_vars[col]
        svar.set(self._get_value(item, col))
        #if col not in self._inplace_widgets:
        self._inplace_widgets[col] = EntryPopup(self, 'enter', textvariable=svar)
        entry = self._inplace_widgets[col]
        entry.place(x=3, y=5, anchor='w', width=20)
        entry.bind('<Unmap>', lambda e: self.__update_value(item, col))
        entry.bind('<FocusOut>', lambda e: self.__update_value(item, col))
        self._inplace_widgets_show[col] = True

    def inplace_checkbutton(self, item, col, onvalue='True', offvalue='False'):
        if col not in self._inplace_vars:
            self._inplace_vars[col] = tk.StringVar()
        svar = self._inplace_vars[col]
        svar.set(self._get_value(item, col))
        if col not in self._inplace_widgets:
            self._inplace_widgets[col] = ttk.Checkbutton(self,
            textvariable=svar, variable=svar, onvalue=onvalue, offvalue=offvalue)
        cb = self._inplace_widgets[col]
        cb.bind('<Unmap>', lambda e: self.__update_value(col, item))
        cb.bind('<FocusOut>', lambda e: self.__update_value(col, item))
        self._inplace_widgets_show[col] = True

    def inplace_combobox(self, col, item, values, readonly=True):
        state = 'readonly' if readonly else 'normal'
        if col not in self._inplace_vars:
            self._inplace_vars[col] = tk.StringVar()
        svar = self._inplace_vars[col]
        svar.set(self._get_value(item, col))
        if col not in self._inplace_widgets:
            self._inplace_widgets[col] = ttk.Combobox(self,
                textvariable=svar, values=values, state=state)
        cb = self._inplace_widgets[col]
        cb.bind('<Unmap>', lambda e: self.__update_value(col, item))
        cb.bind('<FocusOut>', lambda e: self.__update_value(col, item))
        self._inplace_widgets_show[col] = True

    def inplace_spinbox(self, col, item, min, max, step):
        if col not in self._inplace_vars:
            self._inplace_vars[col] = tk.StringVar()
        svar = self._inplace_vars[col]
        svar.set(self._get_value(item, col))
        if col not in self._inplace_widgets:
            self._inplace_widgets[col] = tk.Spinbox(self,
                textvariable=svar, from_=min, to=max, increment=step)
        sb = self._inplace_widgets[col]
        sb.bind('<Unmap>', lambda e: self.__update_value(col, item))
        cb.bind('<FocusOut>', lambda e: self.__update_value(col, item))
        self._inplace_widgets_show[col] = True
        
    def inplace_custom(self, col, item, widget):
        if col not in self._inplace_vars:
            self._inplace_vars[col] = tk.StringVar()
        svar = self._inplace_vars[col]
        svar.set(self._get_value(item, col))
        self._inplace_widgets[col] = widget
        widget.bind('<Unmap>', lambda e: self.__update_value(col, item))
        widget.bind('<FocusOut>', lambda e: self.__update_value(col, item))
        self._inplace_widgets_show[col] = True

# testing
if __name__ == '__main__':
    root = tk.Tk()
    test = AddRecipe('pesto')
    test.wait_window()
    root.destroy()
    root.mainloop()
