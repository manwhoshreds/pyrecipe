# -*- coding: utf-8 -*-
"""
    pyrecipe.console_gui.add_recipe
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A console gui built with urwid used to add recipes to pyrecipe

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""
from collections import deque

import urwid

from pyrecipe import Recipe, db
from pyrecipe.utils import wrap


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
    def __init__(self, ingredients=None, alt_ingredients=None):
        if not ingredients and not alt_ingredients:
            self.ingredients = ['Add ingredient']
        else:
            self.ingredients = ingredients
        self.alt_ingredients = alt_ingredients
        add_ingred_block = urwid.Button('Add Ingredient Block',
                on_press=self._add_block)
        
        add_ingred_block = urwid.GridFlow([add_ingred_block], 24, 0, 0, 'left')
        
        self.ingred_blocks = []
        self.ingred_blocks.append(add_ingred_block)
        if self.ingredients:
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


class EntryBlock(urwid.WidgetWrap):
    """Base class for stacked entry widgets."""
    def __init__(self, entries=[], wrap_amount=70):
        self.widgets = deque()
        wrapped = wrap(entries, wrap_amount)
        
        for index, item in wrapped:
            entry_widget = urwid.Edit(str(index), item)
            self.widgets.append(entry_widget)
        self._refresh()
    
    def _refresh(self, focus_item=0):
        """Refresh the class to reflect changes to the entry stack."""
        self.entry_block = urwid.Pile(self.widgets, focus_item=focus_item)
        super().__init__(self.entry_block)
   
    def keypress(self, size, key):
        """Capture and process a keypress."""
        key = super().keypress(size, key)
        self.row = self.entry_block.focus_position
        try:
            self.col = len(self.widgets[self.row].edit_text) + 2
        except AttributeError:
            # Object has no edit_text attribute. In other words its a 
            # urwid.attr_map() and not a urwid.Edit()
            return key
        pressed = {
                'enter': self.on_enter,
                'ctrl d': self.del_entry,
                'ctrl a': self.insert_entry,
                'ctrl up': self.move_entry,
                'ctrl down': self.move_entry,
                }
        try:
            # I only need to pass key to one function but i will have to pass 
            # to all. This is still a verly clean way to write this as opossed 
            # to if, elif, etc... Perhaps a better way eludes me.
            pressed[key](size, key)
        except KeyError:
            return key
    
    def add_entry(self, button=None):
        """Add an entry to the end of the list."""
        ingred_entry = urwid.Edit("- ", '')
        self.widgets.append(ingred_entry)
        new_focus = len(self.widgets) - 1
        self._refresh(new_focus)
    
    def insert_entry(self, size, key):
        """Insert entry on next line and move cursor."""
        ingred_entry = urwid.Edit("- ", '')
        row_plus = self.row + 1
        self.widgets.insert(row_plus, ingred_entry)
        self.entry_block.move_cursor_to_coords(size, 2, self.row)
        self._refresh(row_plus)

    def del_entry(self, size, key):
        """Delete an entry."""
        widget = self.widgets[self.row]
        self.entry_block.move_cursor_to_coords(size, self.col, self.row)
        item = list(self.widgets)[self.row]
        self.widgets.remove(item)
        if len(self.widgets) == 0:
            self.add_entry()
        try:
            self._refresh(self.row)
        except IndexError:
            # We are at the end of the ingredient list,
            # start deleting goin back
            self._refresh(self.row-1)
    
    def move_entry(self, size, key):
        """Move entry up or down."""
        self.entry_block.move_cursor_to_coords(size, self.col, self.row)
        if key == 'ctrl up':
            widget = self.widgets[self.row-1]
            if isinstance(widget, (urwid.AttrMap, urwid.Padding, urwid.Columns)):
                return
            # up
            newfocus = self.row - 1
        else:
            # down
            newfocus = self.row + 1

        item = self.widgets[self.row]
        self.widgets.remove(item)
        self.widgets.insert(newfocus, item)
        try:
            self._refresh(newfocus)
        except IndexError:
            return
    
    def on_enter(self, size, key):
        """Move cursor to next entry or add an entry if no next entry exists."""
        try:
            col = len(self.widgets[self.row + 1].edit_text) + 2
            self.entry_block.move_cursor_to_coords(size, col, self.row + 1)
        except IndexError:
            self.entry_block.move_cursor_to_coords(size, 2, self.row)
            self.add_entry()
    
    @property
    def widget_list(self):
        """Return a list of widgets from the entry stack."""
        return self.entry_block.widget_list
    
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

class IngredBlock(EntryBlock):
    """Ingredient block for displaying editable ingredients."""
    def __init__(self, ingredients=[], name=None):
        self.ingredients = ingredients
        self.name = name
        self.widgets = deque([BLANK])
        buttons = self._get_buttons()
        self.widgets.append(buttons)
        if name:
            self.alt_name = urwid.AttrMap(urwid.Edit('* ', name), 'title')
            self.widgets.append(self.alt_name)
        
        for item in self.ingredients:
            ingred_entry = urwid.Edit("- ", item)
            self.widgets.append(ingred_entry)
        self._refresh()

    def _get_buttons(self):
        """Get block buttons."""
        add_name = urwid.Button('Toggle Name',
                    on_press=self.toggle_name)
        add_name = urwid.Padding(add_name, 'left', right=10)
        
        del_block = urwid.Button('Delete Block',
                    on_press=self.delete_block)
        del_block = urwid.Padding(del_block, 'left', right=8)
        
        buttons = urwid.Columns([add_name, del_block])
        return buttons
    
    def delete_block(self, button):
        """Delete entire block of ingredients."""
        self.widgets.clear()
        del self.ingredients
        self.name = ''
        self._refresh()
    
    def toggle_name(self, button):
        """Toggle between name for ingredients or no name."""
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
    
    def del_entry(self, size, key):
        """Delete an entry."""
        widget = self.widgets[self.row]
        try:
            # We have an alt_name to account for
            assert isinstance(self.widgets[2], urwid.AttrMap)
            one_ingred_left = 3
        except AssertionError:
            one_ingred_left = 2
        
        self.entry_block.move_cursor_to_coords(size, self.col, self.row)
        item = list(self.widgets)[self.row]
        self.widgets.remove(item)
        if len(self.widgets) == one_ingred_left:
            self.add_entry()
        try:
            self._refresh(self.row)
        except IndexError:
            # We are at the end of the ingredient list,
            # start deleting goin back
            self._refresh(self.row-1)
    
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


class MethodBlock(EntryBlock):
    """Display an editable list of methods."""
    def __init__(self, method=[]):
        self.method = method
        if len(self.method) < 1:
            self.method = ['Add method here.']
        super().__init__(self.method)


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
    def __init__(self, recipe, add=False):
        if add:
            self.r = Recipe()
            self.r['recipe_name'] = recipe
            self.welcome = 'Add a Recipe: {}'.format(self.r['recipe_name'])
        else:
            self.r = recipe
            self.welcome = 'Edit: {}'.format(self.r['recipe_name'])
        
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
        self.disht_group = []
        radio_dish_types = urwid.GridFlow(
            [urwid.AttrMap(
                urwid.RadioButton(self.disht_group, txt), 'buttn', 'buttnf')
                                  for txt in db.DISH_TYPES], 15, 0, 2, 'left'
        )
        for item in self.disht_group:
            if item.get_label() == self.r['dish_type']:
                item.set_state(True)

        self.general_info = [
            urwid.AttrMap(
                urwid.Edit(
                    'Recipe Name: ', 
                    self.r['recipe_name'], 
                    wrap='clip'
                ), 'recipe_name'
            ),
            urwid.AttrMap(
                urwid.IntEdit(
                    'Prep Time: ', 
                    self.r['prep_time']
                ), 'prep_time'
            ),
            urwid.AttrMap(
                urwid.IntEdit(
                    'Cook Time: ', 
                    self.r['cook_time']
                ), 'cook_time'
            ),
            urwid.AttrMap(
                urwid.IntEdit(
                    'Bake Time: ', 
                    self.r['bake_time']
                ), 'bake_time'
            ),
            #urwid.AttrMap(
            #    urwid.Edit(
            #        'Oven Temp: ',
            #        '{} {}'.format(self.r['oven_temp']['amount'],
            #                       self.r['oven_temp']['unit'])
            #    ), 'oven_temp'
            #),
            urwid.AttrMap(
                urwid.Edit(
                    'Price($): ', 
                    self.r['price']
                ), 'price'
            ),
            urwid.AttrMap(
                urwid.Edit(
                    'Source URL: ', 
                    self.r['source_url'], 
                    wrap='clip'
                ), 'source_url'
            ),
            urwid.AttrMap(
                urwid.Edit(
                    'Author: ', 
                    self.r['author']
                ), 'author'
            )
        ]

        self.general_info = urwid.Padding(
            urwid.Pile(self.general_info), align='left', left=2
        )
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
        
        self.ingred_block = IngredientsContainer(
            ingredients=ingreds, alt_ingredients=alt_ingreds
        ) 
        self.method_block = MethodBlock(
            self.r.get_method()
        )
        self.notes_block = NoteBlock(
            self.r['notes']
        )
        general_and_dish = urwid.GridFlow(
            [self.general_info, 
            radio_dish_types, 
            self.notes_block], 53, 0, 2, 'left'
        )
        ingred_and_method = urwid.GridFlow(
            [self.ingred_block, 
            self.method_block], 79, 0, 2, 'left'
        )
        self.listbox_content = [
            BLANK, headings_general_and_dish_types,
            BLANK, general_and_dish,
            BLANK, headings_ingred_and_method,
            BLANK, ingred_and_method
        ]
        list_box = urwid.ListBox(urwid.SimpleListWalker(self.listbox_content))
        return list_box
    
    def quit_prompt(self):
        """Pop-up window that appears when you try to quit."""
        text = "Changes have been made. Quit?"
        question = urwid.Text(("bold", text), "center")
        
        cancel_btn = urwid.AttrMap(urwid.Button(
            "Cancel", self.prompt_answer, "cancel"), "title", None)
        save_btn = urwid.AttrMap(urwid.Button(
            "Save", self.prompt_answer, "save"), "title", None)
        quit_btn = urwid.AttrMap(urwid.Button(
            "Quit", self.prompt_answer, "quit"), "red", None)

        prompt = urwid.LineBox(urwid.ListBox(urwid.SimpleFocusListWalker(
            [question, BLANK, BLANK, cancel_btn, save_btn, quit_btn])))
        
        overlay = urwid.Overlay(
            prompt, self.loop.widget,
            "center", 19, "middle", 9,
            16, 8)
        
        self.loop.widget = overlay 
   
    def test_prompt(self, args):
        """Pop-up window that appears when you try to quit."""
        text = "Changes have been made. Quit?"
        question = urwid.Text(("bold", text), "center")
        
        cancel_btn = urwid.AttrMap(urwid.Button(
            "Cancel", self.test_answer, "cancel"), "title", None)
        save_btn = urwid.AttrMap(urwid.Button(
            "Save", self.test_answer, "save"), "title", None)
        quit_btn = urwid.AttrMap(urwid.Button(
            "Quit", self.test_answer, "quit"), "red", None)

        prompt = urwid.LineBox(urwid.ListBox(urwid.SimpleFocusListWalker(
            [question, BLANK, BLANK, cancel_btn, save_btn, quit_btn])))
        
        overlay = urwid.Overlay(
            prompt, self.loop.widget,
            "center", 19, "middle", 9,
            16, 8)
        self.test.append(IngredBlock(ingredients=['hello'])) 
        self.loop.widget = self.frame
    
    def test_answer(self, button, label):
        """Prompt answer"""
        self.listbox_content = [BLANK]
        self.setup_view()

        self.loop.widget = self.frame
    
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
            if edit_text == '':
                del self.r[attr]
            else: 
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
        
        if len(ingredients) > 0:
            self.r.ingredients = ingredients
        else:
            try: 
                del self.r['ingredients']
            except KeyError:
                pass
        
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
        recipe.save()
        raise urwid.ExitMainLoop()

    def start(self):
        """Main entry point of the recipe editor."""
        self.loop = self.setup_view()
        self.loop.run()
        

if __name__ == '__main__':
    RecipeEditor('test').start()
