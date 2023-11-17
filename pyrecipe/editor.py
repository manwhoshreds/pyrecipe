# -*- coding: utf-8 -*-
"""
    pyrecipe.console_gui.add_recipe
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A console gui built with urwid used to add recipes to pyrecipe

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""
import sys
import copy
import uuid

import urwid as ur

from pyrecipe.backend import DISH_TYPES
from pyrecipe.helpers import wrap


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
    'general_info': ur.AttrMap(ur.Text('General Information:'), 'heading'),
    'dish_types': ur.AttrMap(ur.Text('Dish Types:'), 'heading'),
    'notes': ur.AttrMap(ur.Text('Notes:'), 'heading'),
    'ingredients': ur.AttrMap(ur.Text('Ingredients:'), 'heading'),
    'method': ur.AttrMap(ur.Text('Method:'), 'heading'),
}

BLANK = ur.Divider()


class IngredientsContainer(ur.WidgetWrap):
    """Main container for holding ingredient blocks."""
    def __init__(self, ingredients):
        if not ingredients:
            self.ingredients = {None: [Recipe.ingredient('Add ingredient')]}
        else:
            self.ingredients = ingredients
        
        add_ingred_block = ur.Button('Add Ingredient Block',
                                        on_press=self._add_block)

        add_ingred_block = ur.GridFlow([add_ingred_block], 24, 0, 0, 'left')

        self.ingred_blocks = []
        self.ingred_blocks.append(add_ingred_block)
        for name, ingreds in self.ingredients.items():
            self._add_block(ingreds, name)

    def _add_block(self, ingredients=[], name=None):
        if isinstance(ingredients, ur.Button):
            ingred_block = IngredBlock()
            ingred_block.subscribe_destroy_notify(self)
            self.ingred_blocks.append(ingred_block)
        else:
            ingred_block = IngredBlock(ingredients, name)
            ingred_block.subscribe_destroy_notify(self)
            self.ingred_blocks.append(ingred_block)
        self._refresh()

    def _refresh(self, focus_item=0):
        self.main_container = ur.Pile(self.ingred_blocks, focus_item=focus_item)
        super().__init__(self.main_container)
    
    def destroy_ingredient_block(self):
        if len(self.ingred_blocks) == 2:
            return
        block = self.main_container.focus_position
        self.ingred_blocks.pop(block)
        self._refresh()

    @property
    def blocks(self):
        return self.ingred_blocks[1:]


class IngredientEdit(ur.Edit):
    """Ingredient editor"""

    def __init__(self, ingredient):
        self.ingredient = ingredient
        super().__init__("* ", str(self.ingredient))
    
    
    def get_edit_ingredient(self):
        ingred_str = super().get_edit_text()
        self.ingredient.parse_ingredient(ingred_str)
        return self.ingredient

    
class EntryBlock(ur.WidgetWrap):
    """Base class for stacked entry widgets."""
    
    def __init__(self, entries=[], wrap_amount=70):
        if not entries:
            entries = ['write here']
        self.widgets = []
        wrapped = wrap(entries, wrap_amount)

        for index, item in wrapped:
            entry_widget = ur.Edit(str(index), item)
            self.widgets.append(entry_widget)
        self._refresh()

    def _refresh(self, focus_item=0):
        """Refresh the class to reflect changes to the entry stack."""
        self.pile = ur.Pile(self.widgets, focus_item=focus_item)
        super().__init__(self.pile)

    def keypress(self, size, key):
        """Capture and process a keypress."""
        key = super().keypress(size, key)
        self.row = self.pile.focus_position
        try:
            self.col = len(self.widgets[self.row].edit_text) + 2
        except AttributeError:
            # Object has no edit_text attribute. In other words its a
            # ur.attr_map() and not a ur.Edit()
            return key
        pressed = {
            'enter': self.on_enter,
            'ctrl d': self.del_entry,
        }
        try:
            pressed[key](size, key)
        except KeyError:
            return key
    
    def add_entry(self, button=None):
        """Add an entry to the end of the list."""
        caption = str(len(self.widgets) + 1) + '. '
        entry = ur.Edit(caption, '')
        self.widgets.append(entry)
        new_focus = len(self.widgets) - 1
        self._refresh(new_focus)

    def del_entry(self, size, key):
        """Delete an entry."""
        widget = self.widgets[self.row]
        self.pile.move_cursor_to_coords(size, self.col, self.row)
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

    def on_enter(self, size, key):
        """Move cursor to next entry or add an entry if no next entry exists."""
        try:
            col = len(self.widgets[self.row + 1].edit_text) + 2
            self.pile.move_cursor_to_coords(size, col, self.row + 1)
        except IndexError:
            self.pile.move_cursor_to_coords(size, 2, self.row)
            self.add_entry()

    
    @property
    def widget_list(self):
        """Return a list of widgets from the entry stack."""
        return self.pile.widget_list

    def get_entries(self):
        """Retrieve the text from the entries."""
        entries = []
        for item in self.widget_list:
            text = item.get_edit_text()
            text = ' '.join(text.split())
            entries.append(text)
        return entries


class IngredBlock(EntryBlock):
    """Ingredient block for displaying editable ingredients."""
    
    def __init__(self, ingredients=[], name=None):
        if ingredients:
            self.ingredients = ingredients
        else:
            self.ingredients = [Recipe.ingredient("add")]
        self.name = name
        self.widgets = [BLANK]
        self.widgets.append(self._get_buttons())
        if name:
            self.named_name = ur.AttrMap(ur.Edit('* ', name), 'title')
            self.widgets.append(self.named_name)
        
        self.ingredient_container = None
        
        for item in self.ingredients:
            ingred_entry = IngredientEdit(item)
            self.widgets.append(ingred_entry)
        self._refresh()

    
    def _get_buttons(self):
        """Get block buttons."""
        add_name = ur.Button('Toggle Name', on_press=self.toggle_name)
        add_name = ur.Padding(add_name, 'left', right=10)
        del_block = ur.Button('Delete Block', on_press=self.delete_block)
        del_block = ur.Padding(del_block, 'left', right=8)
        buttons = ur.Columns([add_name, del_block])
        return buttons

    def subscribe_destroy_notify(self, ingredient_container):
        self.ingredient_container = ingredient_container
        
    def keypress(self, size, key):
        """Capture and process a keypress."""
        key = super().keypress(size, key)
        self.row = self.pile.focus_position
        try:
            self.col = len(self.widgets[self.row].edit_text) + 2
        except AttributeError:
            # Object has no edit_text attribute. In other words its a
            # ur.attr_map() and not a ur.Edit()
            return key
        pressed = {
            'enter': self.on_enter,
            'ctrl d': self.del_entry,
            'ctrl a': self.insert_entry,
            'ctrl up': self.move_entry,
            'ctrl down': self.move_entry,
        }
        try:
            # The closest thing to php's switch statement that I can think of.
            pressed[key](size, key)
        except KeyError:
            return key
    
    def move_entry(self, size, key):
        """Move entry up or down."""
        self.pile.move_cursor_to_coords(size, self.col, self.row)
        if key == 'ctrl up':
            widget = self.widgets[self.row-1]
            if isinstance(widget, (ur.AttrMap, ur.Padding, ur.Columns)):
                return
            # up
            newfocus = self.row - 1
        else:
            # down
            newfocus = self.row + 1
        item = self.widgets.pop(self.row)
        self.widgets.insert(newfocus, item)
        try:
            self._refresh(newfocus)
        except IndexError:
            return
    

    def add_entry(self, button=None):
        """Add an entry to the end of the list."""
        ingredient = Recipe.ingredient('')
        ingredient.group_name = self.name
        ingred_entry = IngredientEdit(ingredient)
        self.widgets.append(ingred_entry)
        new_focus = len(self.widgets) - 1
        self._refresh(new_focus)
    

    def delete_block(self, button):
        """Delete entire block of ingredients."""
        self.ingredient_container.destroy_ingredient_block()
    
    def toggle_name(self, button):
        """Toggle between name for ingredients or no name."""
        if not self.name:
            self.named_name = ur.AttrMap(ur.Edit('* ', 'Name'), 'title')
            self.widgets.insert(2, self.named_name)
            self.name = self.named_name.original_widget.get_edit_text()
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

    
    def insert_entry(self, size, key):
        """Insert entry on next line and move cursor."""
        ingred_entry = IngredientEdit(Recipe.ingredient(''))
        row_plus = self.row + 1
        self.widgets.insert(row_plus, ingred_entry)
        self.pile.move_cursor_to_coords(size, 2, self.row)
        self._refresh(row_plus)
    

    def del_entry(self, size, key):
        """Delete an entry."""
        try:
            # We have an alt_name to account for
            assert isinstance(self.widgets[2], ur.AttrMap)
            one_ingred_left = 3
        except AssertionError:
            one_ingred_left = 2
        
        self.pile.move_cursor_to_coords(size, self.col, self.row)
        
        widget = self.widgets[self.row]
        self.widgets.remove(widget)
        
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
        for item in self.widgets:
            if isinstance(item, ur.AttrMap):
                self.name = item.original_widget.get_edit_text()
                continue
            if isinstance(item, IngredientEdit):
                ingred = item.get_edit_ingredient()
                ingred.group_name = self.name
                ingredients.append(ingred)
        return ingredients



class RecipeEditor:
    """The pyrecipe console interface for managing recipes."""
    
    footer_text = ('foot', [
        ('pyrecipe', ' PYRECIPE    '),
        ('key', "F2"), ('footer', ' Save  '),
        ('key', "Esc"), ('footer', ' Quit  '),
        ('key', "Ctrl-UP/DOWN"), ('footer', ' Move ingredient UP/DOWN  '),
        ('key', "Ctrl-a"), ('footer', ' Insert ingredient  '),
        ('key', "Ctrl-d"), ('footer', ' Delete item  ')
    ])
    
    def __init__(self, recipe):
        self.recipe = recipe
        
        if self.recipe.has_id:
            # Recipe has ID which must mean it exist in the database
            self.welcome = f'Edit: {self.recipe.name} ({self.recipe.recipe_id})'
        else:
            self.welcome = f'Add a Recipe: {self.recipe.name}'
            self.recipe.uuid = str(uuid.uuid4())
        
        self.initial_state = self.recipe.dump_data()
        self.original_name = self.recipe.name

    
    def setup_view(self):
        header = ur.AttrMap(ur.Text(self.welcome), 'header')
        listbox = self.setup_listbox()
        self.frame = ur.Frame(ur.AttrMap(listbox, 'body'), header=header)
        self.frame.footer = ur.AttrMap(ur.Text(self.footer_text), 'footer')
        loop = ur.MainLoop(self.frame, palette=PALETTE)
        loop.unhandled_input = self.handle_input
        loop.pop_ups = True
        return loop
   
    
    def _get_general_info(self):
        """General info editors."""
        general_info = [
            ur.AttrMap(ur.Edit('Recipe Name: ', self.recipe.name, 
                                wrap='clip'), 'name'
                                ),
            ur.AttrMap(ur.IntEdit('Prep Time: ', 
                                  self.recipe.prep_time), 
                                  'prep_time'
                                  ),
            ur.AttrMap(ur.IntEdit('Cook Time: ',
                                  self.recipe.cook_time), 'cook_time'
                                  ),
            ur.AttrMap(ur.Edit('Source URL: ',
                                     self.recipe.source_url,
                                     wrap='clip'), 'source_url'
                                     ),
            ur.AttrMap(ur.Edit('Author: ',
                                self.recipe.author), 'author'
                                )
        ]
        return general_info
    
    
    def setup_listbox(self):
        """The main listbox"""
        self.disht_group = []
        radio_dish_types = ur.GridFlow(
            [ur.AttrMap(
                ur.RadioButton(self.disht_group, txt), 'buttn', 'buttnf')
                                for txt in DISH_TYPES], 15, 0, 2, 'left'
        )
        for item in self.disht_group:
            if item.get_label() == self.recipe.dish_type:
                item.set_state(True)

        self.general_info = self._get_general_info()

        self.general_info = ur.Padding(
            ur.Pile(self.general_info), align='left', left=2
        )
        headings_general_and_dish_types = ur.GridFlow(
                    [HEADINGS['general_info'],
                     HEADINGS['dish_types'],
                     HEADINGS['notes'],
                     ], 53, 0, 2, 'left'
        )
        headings_ingred_and_method = ur.GridFlow(
                    [HEADINGS['ingredients'],
                     HEADINGS['method'],
                     ], 79, 0, 2, 'left'
        )

        self.ingred_block = IngredientsContainer(
            ingredients = self.recipe.get_ingredients()
        )
        
        self.method_block = EntryBlock(
            self.recipe.steps
        )
        
        self.notes_block = EntryBlock(
            self.recipe.notes
        )
        
        general_and_dish = ur.GridFlow(
            [self.general_info,
            radio_dish_types,
            self.notes_block], 53, 0, 2, 'left'
        )
        
        ingred_and_method = ur.GridFlow(
            [self.ingred_block,
            self.method_block], 79, 0, 2, 'left'
        )
        
        self.listbox_content = [
            BLANK, headings_general_and_dish_types,
            BLANK, general_and_dish,
            BLANK, headings_ingred_and_method,
            BLANK, ingred_and_method
        ]
        list_box = ur.ListBox(ur.SimpleListWalker(self.listbox_content))
        return list_box

    
    def quit_prompt(self):
        """Pop-up window that appears when you try to quit."""
        text = "Changes have been made. Quit?"
        question = ur.Text(("bold", text), "center")

        cancel_btn = ur.AttrMap(ur.Button(
            "Cancel", self.prompt_answer, "cancel"), "title", None)
        save_btn = ur.AttrMap(ur.Button(
            "Save", self.prompt_answer, "save"), "title", None)
        quit_btn = ur.AttrMap(ur.Button(
            "Quit", self.prompt_answer, "quit"), "red", None)

        prompt = ur.LineBox(ur.ListBox(ur.SimpleFocusListWalker(
            [question, BLANK, BLANK, cancel_btn, save_btn, quit_btn])))

        overlay = ur.Overlay(
            prompt, self.loop.widget,
            "center", 19, "middle", 9,
            16, 8)

        self.loop.widget = overlay

    
    def prompt_answer(self, button, label):
        """Prompt answer"""
        if label == 'quit':
            sys.exit()
        elif label == 'save':
            self.save_recipe()
        else:
            self.loop.widget = self.frame

    
    def handle_input(self, key):
        """Handle the input."""
        if key in ('f8', 'esc'):
            if self.recipe_changed:
                self.quit_prompt()
                return
            else:
                raise ur.ExitMainLoop()
        elif key in ('f2',):
            self.save_recipe()
        elif key in ('f3',):
            self.save_recipe(debug=True)
        else:
            pass

    
    @property
    def recipe_changed(self):
        """Check if the state of the recipe has changed."""
        changed = False
        self.update_recipe_data()
        if self.initial_state != self.recipe.dump_data():
            changed = True
        return changed

    
    def update_recipe_data(self):
        """Grab the data from the editors."""
        # gen info
        gen_info = self.general_info.original_widget.widget_list
        for item in gen_info:
            attr = item.attr_map[None]
            edit_text = item.original_widget.get_edit_text()
            try:
                edit_text = int(edit_text)
            except ValueError:
                pass
            self.recipe[attr] = edit_text

        for item in self.disht_group:
            if item.get_state() == True:
                self.recipe.dish_type = item.get_label()

        # ingredients
        ingredients = []
        for block in self.ingred_block.blocks:
            ingreds = block.get_ingredients()
            ingredients += ingreds
        self.recipe.ingredients = ingredients
        
        # method
        self.recipe.steps = self.method_block.get_entries()

        # notes if any
        notes = self.notes_block.get_entries()
        if notes:
            self.recipe.notes = notes
    
    
    def save_recipe(self, debug=False):
        """Save the current state of the recipe and exit."""
        self.update_recipe_data()
        if not debug:
            raise ur.ExitMainLoop()

    
    def start(self):
        """Main entry point of the recipe editor."""
        self.loop = self.setup_view()
        self.loop.run()
        return self.recipe


if __name__ == '__main__':
    pass
