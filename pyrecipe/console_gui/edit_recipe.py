# -*- coding: utf-8 -*-
"""
    pyrecipe.console_gui.add_recipe
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A console gui built with urwid used to add recipes to pyrecipe

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""
import textwrap
from collections import deque

import urwid

from pyrecipe.config import (DISH_TYPES)
from pyrecipe.recipe import Recipe, IngredientParser
from pyrecipe.utils import wrap


ingred_parser = IngredientParser()

PALETTE = ([
    ('header', 'white', 'black', 'bold'),
    ('footer', 'white', 'black', 'bold'),
    ('foot', 'white', 'black', 'bold'),
    ('heading', 'dark cyan', 'black'),
    ('key', 'light cyan', 'black'),
    ('title', 'light cyan', 'default'),
    ('red', 'light red', 'default', 'bold'),
    ('pyrecipe', 'light green', 'black'),
    ('button', 'yellow', 'dark green', 'standout'),
    ])

HEADINGS = {
            'general_info': urwid.AttrMap(urwid.Text('General Information:'), 'heading'),
            'dish_types': urwid.AttrMap(urwid.Text('Dish Types:'), 'heading'),
            'notes': urwid.AttrMap(urwid.Text('Notes:'), 'heading'),
            'ingredients': urwid.AttrMap(urwid.Text('Ingredients:'), 'heading'),
            'method': urwid.AttrMap(urwid.Text('Method:'), 'heading'),
            }

BLANK = urwid.Divider()


class IngredientsContainer(urwid.WidgetWrap):
    """Main container for holding ingredient blocks."""

    def __init__(self, ingredients=[], alt_ingredients=None):
        self.ingredients = ingredients
        self.alt_ingredients = alt_ingredients
        if not isinstance(self.ingredients, list):
            raise TypeError('IngredientBlock only excepts a list of ingredients')

        add_ingred_block = urwid.Button('Add Ingredient Block',
                on_press=self._add_block)
        
        add_ingred_block = urwid.GridFlow([add_ingred_block], 24, 0, 0, 'left')
        
        self.ingred_blocks = []
        self.ingred_blocks.append(add_ingred_block)
        self._add_block(self.ingredients)
        if self.alt_ingredients:
            for item in self.alt_ingredients:
                ingreds = self.alt_ingredients[item]
                self._add_block(ingredients=ingreds, name=item)
    
    def _add_block(self, ingredients=[], name=None):
        if isinstance(ingredients, urwid.Button):
            ingred_block = IngredBlock()
            self.ingred_blocks.append(ingred_block)
        else: 
            ingred_block = IngredBlock(ingredients, name)
            self.ingred_blocks.append(ingred_block)
        try:
            new_focus = len(self.ingred_blocks) - 1
        except AttributeError:
            new_focus = 0
        self._refresh(new_focus)
    
    def _refresh(self, focus_item=0):
        self.main_container = urwid.Pile(self.ingred_blocks, focus_item=focus_item)
        super().__init__(self.main_container)
    
    @property
    def blocks(self):
        return self.ingred_blocks[1:]


class IngredBlock(urwid.WidgetWrap):
    """Ingredient block for displaying editable ingredients."""
    def __init__(self, ingredients=[], name=None):
        self.ingredients = ingredients
        self.name = name
        if not isinstance(self.ingredients, list):
            raise TypeError('IngredBlock only excepts a list of ingredients')
        
        self.widgets = deque([BLANK])
        buttons = self._get_buttons()
        self.widgets.append(buttons)
        if name:
            self.alt_name = urwid.AttrMap(urwid.Edit('* ', name), 'title')
            self.widgets.append(self.alt_name)
        
        if len(self.ingredients) < 1:
            ingred_entry = urwid.Edit("- ", 'add ingredient')
            self.widgets.append(ingred_entry)
        else:
            for item in self.ingredients:
                ingred_entry = urwid.Edit("- ", item)
                self.widgets.append(ingred_entry)
        self._refresh()

    def _refresh(self, focus_item=0):
        self.ingred_block = urwid.Pile(self.widgets, focus_item=focus_item)
        super().__init__(self.ingred_block)
    
    def _get_buttons(self):
        add_button = urwid.Button('Add Ingredient',
                    on_press=self.add_ingredient)
        add_button = urwid.Padding(add_button, 'left', right=8)
        
        add_name = urwid.Button('Toggle Name',
                    on_press=self.toggle_name)
        add_name = urwid.Padding(add_name, 'left', right=10)
        
        del_block = urwid.Button('Delete Block',
                    on_press=self.delete_block)
        del_block = urwid.Padding(del_block, 'left', right=8)
        buttons = urwid.Columns([add_button, 
                                 add_name,
                                 del_block
                                ])
        return buttons
    
    def delete_block(self, button):
        self.widgets.clear()
        del self.ingredients
        self.name = ''
        self._refresh()

    def toggle_name(self, button):
        if not self.name:
            self.alt_name = urwid.AttrMap(urwid.Edit('* ', 'Name'), 'title')
            self.widgets.insert(2, self.alt_name)
            self.name = self.alt_name.original_widget.get_edit_text()
            self._refresh(2)
        else:
            for item in self.widgets:
                try:
                    if item.attr_map[None] == 'title':
                        self.widgets.remove(item)
                        self.name = None
                        break
                except AttributeError:
                    pass
            self._refresh(2)

    def keypress(self, size, key):
        key = super().keypress(size, key)
        self.row = self.ingred_block.focus_position
        try: 
            self.end_col = len(self.widgets[self.row].edit_text) + 2
        except:
            return key
        
        pressed = {
                'enter': self.on_enter,
                'ctrl d': self.del_ingredient,
                'ctrl a': self.insert_ingredient,
                'ctrl up': self.move_entry,
                'ctrl down': self.move_entry,
                }
        try:
            # I only need to pass key to one function
            # but i will have to pass to all
            # this is still a verly clean way to write this
            # as opossed to if, elif, etc....
            # perhaps a better way eludes me
            pressed[key](size, key)
        except KeyError:
            return key
    
    def add_ingredient(self, button=None):
        ingred_entry = urwid.Edit("- ", '')
        self.widgets.append(ingred_entry)
        new_focus = len(self.widgets) - 1
        self._refresh(new_focus)
    
    def insert_ingredient(self, size, key):
        ingred_entry = urwid.Edit("- ", '')
        row_plus = self.row + 1
        self.widgets.insert(row_plus, ingred_entry)
        self.ingred_block.move_cursor_to_coords(size, 2, self.row)
        self._refresh(row_plus)

    def del_ingredient(self, size, key):
        widget = self.widgets[self.row]
        if isinstance(widget, (urwid.AttrMap, urwid.Padding, urwid.Columns)):
            return
        row_minus_one = self.row - 1
        row_minus_one = self.widgets[row_minus_one]
        if isinstance(row_minus_one, (urwid.AttrMap, urwid.Columns)):
            return

        try: 
            row = self.row
            col = len(self.widgets[row].edit_text) + 2
        except IndexError:
            row = self.row
            col = len(self.widgets[row].edit_text) - 2

        self.ingred_block.move_cursor_to_coords(size, col, row)
        try: 
            item = list(self.widgets)[self.row]
            self.widgets.remove(item)
        except IndexError:
            pass
        self._refresh(self.row-1)

    def move_entry(self, size, key):
        try: 
            row = self.row
            col = len(self.widgets[row].edit_text) + 2
        except IndexError:
            row = self.row
            col = len(self.widgets[row].edit_text) - 2
        
        self.ingred_block.move_cursor_to_coords(size, col, row)
        if key == 'ctrl up':
            widget = self.widgets[self.row-1]
            if isinstance(widget, (urwid.AttrMap, urwid.Padding, urwid.Columns)):
                return
            # up
            newfocus = self.row - 1
        else:
            # down
            newfocus = self.row + 1

        item = list(self.widgets)[self.row]
        self.widgets.remove(item)
        self.widgets.insert(newfocus, item)
        try:
            self._refresh(newfocus)
        except IndexError:
            return
    
    def on_enter(self, size, key):
        try:
            col = len(self.widgets[self.row + 1].edit_text) + 2
            self.ingred_block.move_cursor_to_coords(size, col, self.row + 1)
        except IndexError:
            self.ingred_block.move_cursor_to_coords(size, 2, self.row)
            self.add_ingredient()

    def get_ingredients(self):
        ingredients = []
        alt_ingreds = {}
        for item in self.widgets:
            if isinstance(item, urwid.AttrMap):
                self.name = item.original_widget.get_edit_text()
            if isinstance(item, urwid.Edit):
                ingredients.append(item.get_edit_text())
        
        if self.name:
            alt_ingreds[self.name] = ingredients
            return alt_ingreds
        else:
            return ingredients


class EntryBlock(urwid.WidgetWrap):
    """Base class for entry piles."""
    def __init__(self, entries=[], wrap_amount=70):
        self.widgets = deque()
        if not isinstance(entries, list):
            raise TypeError('{} only excepts a list of methods'.format(__class__))
        
        wrapped = wrap(entries, wrap_amount)
        for index, item in wrapped:
            method_entry = urwid.Edit(str(index) + ' ', item)
            self.widgets.append(method_entry)
        self._refresh()

    def _refresh(self, focus_item=0):
        self.pile = urwid.Pile(self.widgets, focus_item=focus_item)
        super().__init__(self.pile)
    
    @property
    def widget_list(self):
        return self.pile.widget_list
    
    def keypress(self, size, key):
        key = super().keypress(size, key)
        self.row = self.pile.focus_position
        try: 
            self.end_col = len(self.widgets[self.row].edit_text) + 2
        except:
            return key
        
        pressed = {
                'enter': self.on_enter,
                'ctrl d': self.del_entry,
                'ctrl up': self.move_entry,
                'ctrl down': self.move_entry
                }
        try:
            pressed[key](size, key)
        except KeyError:
            return key
    
    def add_entry(self):
        """Add an entry."""
        caption = str(len(self.widgets) + 1)
        entry = urwid.Edit(caption + ". ", '')
        self.widgets.append(entry)
        new_focus = len(self.widgets) - 1
        self._refresh(focus_item=new_focus)
    
    def del_entry(self, size, key):
        """Delete an entry."""
        if len(self.widgets) == 1:
            return
        row_minus_one = self.row - 1
        row_minus_one = self.widgets[row_minus_one]
        if isinstance(row_minus_one, (urwid.AttrMap, urwid.Columns)):
            return

        try: 
            row = self.row
            col = len(self.widgets[row].edit_text) + 2
        except IndexError:
            row = self.row
            col = len(self.widgets[row].edit_text) - 2

        self.pile.move_cursor_to_coords(size, col, row)
        try: 
            item = list(self.widgets)[self.row]
            self.widgets.remove(item)
        except IndexError:
            pass
        self._refresh(self.row-1)
    
    def move_entry(self):
        """Move an entry up or down."""
        pass
        
    def on_enter(self, size, key):
        """Respond to the enter key."""
        try:
            col = len(self.widgets[self.row + 1].edit_text) + 2
            self.pile.move_cursor_to_coords(size, col, self.row + 1)
        except IndexError:
            self.pile.move_cursor_to_coords(size, 2, self.row)
            self.add_entry()

    def get_entries(self):
        """Retrieve the text from the entries."""
        entries = []
        for item in self.widget_list:
            if isinstance(item, urwid.GridFlow):
                continue
            text = item.get_edit_text()
            text = ' '.join(text.split())
            entries.append(text)
        return entries


class MethodBlock(EntryBlock):
    """Display an editable list of methods."""
    def __init__(self, method=[]):
        self.method = method
        if len(self.method) < 1:
            self.method = ['Add method here.']
        super().__init__(self.method)

    def get_method(self):
        pass
        

class MethodBlockBAK(urwid.WidgetWrap):
    """Display an editable list of methods."""
    def __init__(self, method=[]):
        self.method_widgets = deque()
        self.method = method
        if not isinstance(self.method, list):
            raise TypeError('MethodBlock only excepts a list of methods')
        
        add_button = urwid.Button('Add Method',
                on_press=self.add_method)
        self.method_widgets.append(urwid.GridFlow([add_button], 14, 0, 0, 'left'))
        
        wrapped = wrap(self.method)
        for index, item in wrapped:
            method_entry = urwid.Edit(str(index) + ' ', item)
            self.method_widgets.append(method_entry)
            
        if len(self.method_widgets) > 0:
            method_pile = urwid.Pile(self.method_widgets)
        else:
            method_pile = BLANK
        self._refresh()

    def _refresh(self, focus_item=1):
        try:
            self.pile = urwid.Pile(self.method_widgets, focus_item=focus_item)
        except IndexError:
            self.pile = urwid.Pile(self.method_widgets, focus_item=focus_item-1)
        self.num_widgets = len(self.method_widgets)
        super().__init__(self.pile)
    
    def _renumber(self, focus_item=1):
        self.method_widgets.clear()
        wrapped = wrap(self.method)
        for index, item in wrapped:
            method_entry = urwid.Edit(str(index) + ' ', item)
            self.method_widgets.append(method_entry)
        try:
            self.pile = urwid.Pile(self.method_widgets, focus_item=focus_item)
        except IndexError:
            self.pile = urwid.Pile(self.method_widgets, focus_item=focus_item-1)
        self.num_widgets = len(self.method_widgets)
        super().__init__(self.pile)

    def add_method(self, button):
        caption = str(len(self.method_widgets))
        method_entry = urwid.Edit(caption + ". ", '')
        self.method_widgets.append(method_entry)
        new_focus = len(self.method_widgets) - 1
        self._refresh(focus_item=new_focus)
    
    def del_method(self, size):
        # dont let the user delete the add button at pos 0
        if self.focus_pos == 0:
            return
        if self.num_widgets == 2:
            self.method_widgets[1].edit_text = 'add method'
            return
        try: 
            row = self.focus_pos + 1
            col = len(self.method_widgets[row].edit_text) + 2
        except IndexError:
            row = self.focus_pos - 1
            col = len(self.method_widgets[row].edit_text) - 2

        self.pile.move_cursor_to_coords(size, col, row)
        try: 
            item = list(self.method_widgets)[self.focus_pos]
            self.method_widgets.remove(item)
        except IndexError:
            pass
        self._refresh(self.focus_pos)
        #self._renumber(self.focus_pos)
    
    @property
    def widget_list(self):
        return self.pile.widget_list

    def keypress(self, size, key):
        self.focus_pos = self.pile.focus_position
        key = super().keypress(size, key)
        if key == 'enter':
            self.on_enter(key)
        elif key == 'ctrl d':
            self.del_method(size)
        else:
            return key

    def on_enter(self, key):
        try:
            self.pile.set_focus(self.focus_pos + 1)
        except IndexError:
            pass
    
    def get_entries(self):
        entries = []
        for item in self.widget_list:
            if isinstance(item, urwid.GridFlow):
                continue
            text = item.get_edit_text()
            text = ' '.join(text.split())
            entries.append(text)
        return entries


class NoteBlock(EntryBlock):
    """Display an editable list of notes."""
    def __init__(self, notes=[]):
        self.notes = notes
        if len(self.notes) < 1:
            self.notes = ['No notes added yet']
        super().__init__(self.notes, wrap_amount=45)

    def get_entries(self):
        """Get text from the entries."""
        entries = []
        for item in self.widget_list:
            if isinstance(item, urwid.GridFlow):
                continue
            text = item.get_edit_text()
            text = ' '.join(text.split())
            entries.append(text)
        if entries[0] == 'No notes added yet':
            entries = ''
        return entries


class RecipeEditor:
    """The pyrecipe console interface for managing recipes."""
    footer_text = ('foot', [
        ('pyrecipe', ' PYRECIPE    '),
        ('key', "F2"), ('footer', ' Save  '),
        ('key', "Esc"), ('footer', ' Quit  '),
        ('key', "Ctrl-UP/DOWN"), ('footer', ' Move item UP/DOWN  '),
        ('key', "Ctrl-a"), ('footer', ' Insert item  '),
        ('key', "Ctrl-d"), ('footer', ' Delete item  ')
        ])
    def __init__(self, recipe='', add=False):
        self.add = add
        if self.add:
            if isinstance(recipe, Recipe):
                self.r = recipe
            else:
                self.r = Recipe()
                self.r['recipe_name'] = recipe
            self.welcome = 'Add a Recipe: {}'.format(self.r['recipe_name'])
        else:
            self.r = Recipe(recipe)
            self.welcome = 'Edit: {}'.format(self.r['recipe_name'])
        
        self.disht_group = []
        self.initial_hash = hash(self.r)
        self.data = self.r['_recipe_data']

    def setup_view(self):
        header = urwid.AttrMap(urwid.Text(self.welcome), 'header')
        listbox = self.setup_listbox()
        self.frame = urwid.Frame(urwid.AttrMap(listbox, 'body'), header=header)
        self.frame.footer = urwid.AttrMap(urwid.Text(
            self.footer_text), 'footer')
        loop = urwid.MainLoop(self.frame, palette=PALETTE)
        loop.unhandled_input = self.handle_input
        loop.pop_ups = True
        return loop
    
    def setup_listbox(self):
        """The main listbox"""
        #radio_dish_types = urwid.Pile([urwid.AttrMap(urwid.RadioButton(self.disht_group,
        #                    txt), 'buttn', 'buttnf')
        #                    for txt in DISH_TYPES])

        radio_dish_types = urwid.GridFlow([urwid.AttrMap(urwid.RadioButton(self.disht_group,
                            txt), 'buttn', 'buttnf')
                            for txt in DISH_TYPES], 15, 0, 2, 'left')
        
        for item in self.disht_group:
            if item.get_label() == self.r['dish_type']:
                item.set_state(True)

        self.general_info = [urwid.AttrMap(
                                urwid.Edit('Recipe Name: ', self.r['recipe_name'], wrap='clip'), 'recipe_name'),
                             urwid.AttrMap(urwid.IntEdit('Prep Time: ', self.r['prep_time']), 'prep_time'),
                             urwid.AttrMap(urwid.IntEdit('Cook Time: ', self.r['cook_time']), 'cook_time'),
                             urwid.AttrMap(urwid.IntEdit('Bake Time: ', self.r['bake_time']), 'bake_time'),
                             urwid.AttrMap(urwid.Edit('Price($): ', self.r['price']), 'price'),
                             urwid.AttrMap(urwid.Edit('Source URL: ', self.r['source_url'], wrap='clip'), 'source_url'),
                             urwid.AttrMap(urwid.Edit('Author: ', self.r['author']), 'author')]
                             #urwid.AttrMap(urwid.Edit('Categories (comma separated): ', self.r['categories']), 'categories')]

        self.general_info = urwid.Padding(urwid.Pile(self.general_info), align='left', left=2)
        
        headings_general_and_dish_types = urwid.GridFlow(
                    [HEADINGS['general_info'], 
                     HEADINGS['dish_types'],
                     HEADINGS['notes'],
                     ], 53, 0, 2, 'left'
                )
        headings_ingred_and_method = urwid.GridFlow(
                    [HEADINGS['ingredients'], 
                     HEADINGS['method'],
                     ], 79, 0, 2, 'left'
                )
         
        ingreds, alt_ingreds = self.r.get_ingredients()
        self.ingred_block = IngredientsContainer(ingredients=ingreds, alt_ingredients=alt_ingreds) 
        self.method_block = MethodBlock(self.r.get_method())
        self.notes_block = NoteBlock(self.r['notes'])
        
        general_and_dish = urwid.GridFlow([self.general_info, radio_dish_types, self.notes_block], 53, 0, 2, 'left')
        ingred_and_method = urwid.GridFlow([self.ingred_block, self.method_block], 79, 0, 2, 'left')
        
        self.listbox_content = [
                BLANK,
                headings_general_and_dish_types,
                BLANK,
                general_and_dish,
                BLANK,
                headings_ingred_and_method,
                BLANK,
                ingred_and_method
                ]
        
        list_box = urwid.ListBox(urwid.SimpleListWalker(self.listbox_content))
        
        return list_box
    
    def quit_prompt(self):
        """Pop-up window that appears when you try to quit."""
        text = "Changes have been made. Quit?"
        question = urwid.Text(("bold", text), "center")
        quit_btn = urwid.AttrMap(urwid.Button(
            "Quit", self.prompt_answer, "quit"), "red", None)
        save_btn = urwid.AttrMap(urwid.Button(
            "Save", self.prompt_answer, "save"), "title", None)
        cancel_btn = urwid.AttrMap(urwid.Button(
            "Cancel", self.prompt_answer, "cancel"), "title", None)

        prompt = urwid.LineBox(urwid.ListBox(urwid.SimpleFocusListWalker(
            [question, BLANK, BLANK, quit_btn, save_btn, cancel_btn])))
        
        overlay = urwid.Overlay(
            prompt, self.loop.widget,
            "center", 19, "middle", 9,
            16, 8)
        
        self.loop.widget = overlay 
   
    def prompt_answer(self, button, label):
        """Prompt answer"""
        if label == 'quit':
            raise urwid.ExitMainLoop()
        elif label == 'save':
            self.save_recipe()
        else:
            self.loop.widget = self.frame

    def handle_input(self, key):
        """Handle the input."""
        if key in ('f8', 'esc'):
            if self.recipe_changed:
                self.quit_prompt()
                #self.test_prompt()
                return
            else:
                raise urwid.ExitMainLoop()
        elif key in ('f2',):
            self.save_recipe()
        else:
            pass
   
    @property
    def recipe_changed(self):
        """Check if the state of the recipe has changed."""
        changed = False
        recipe = self.get_recipe_data()
        if self.initial_hash != hash(recipe):
            changed = True
        return changed
    
    def get_recipe_data(self):
        """Grab the data from the editors."""
        # gen info
        gen_info = self.general_info.original_widget.widget_list
        for item in gen_info:
            attr = item.attr_map[None]
            edit_text = item.original_widget.get_edit_text()
            if edit_text != '':
                self.r[attr] = edit_text
         
        for item in self.disht_group:
            if item.get_state() == True:
                self.r['dish_type'] = item.get_label()
        
        # ingredients
        ingredients = []
        alt_ingreds = []
        names = []
        for block in self.ingred_block.blocks:
            ingreds = block.get_ingredients()
            if isinstance(ingreds, dict):
                alt_ingreds.append(ingreds)
                names += list(ingreds.keys())
            else:
                ingredients += ingreds
        self.r.ingredients = ingredients
        
        if len(alt_ingreds) > 0:
            self.r.alt_ingredients = alt_ingreds
        else:
            try: 
                del self.r['alt_ingredients']
            except KeyError:
                pass
         
        # method
        steps = []
        method_entries = self.method_block.get_entries()
        for item in method_entries:
            steps.append({'step': item})
        self.r['steps'] = steps

        # notes if any
        notes = self.notes_block.get_entries()
        if notes:
            self.r['notes'] = notes
        return self.r
    
    def save_recipe(self):
        """Save the current state of the recipe and exit."""
        recipe = self.get_recipe_data()
        if self.add:
            recipe.save(save_as=True)
        else:
            recipe.save()
        raise urwid.ExitMainLoop()

    def start(self):
        """Main entry point of the recipe editor."""
        self.loop = self.setup_view()
        self.loop.run()
        

if __name__ == '__main__':
    RecipeEditor('test').start()
