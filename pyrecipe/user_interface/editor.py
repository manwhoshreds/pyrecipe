# -*- coding: utf-8 -*-
"""
    pyrecipe.console_gui.add_recipe
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A console gui built with urwid used to add recipes to pyrecipe

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""
import copy
from collections import deque
import uuid

import urwid as ur

from pyrecipe.db import RecipeDB, DBInfo, DISH_TYPES
from pyrecipe.recipe import Recipe
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
    'general_info': ur.AttrMap(ur.Text('General Information:'), 'heading'),
    'dish_types': ur.AttrMap(ur.Text('Dish Types:'), 'heading'),
    'notes': ur.AttrMap(ur.Text('Notes:'), 'heading'),
    'ingredients': ur.AttrMap(ur.Text('Ingredients:'), 'heading'),
    'method': ur.AttrMap(ur.Text('Method:'), 'heading'),
}

BLANK = ur.Divider()


class IngredientsContainer(ur.WidgetWrap):
    """Main container for holding ingredient blocks."""
    def __init__(self, ingredients=None, named_ingredients=None):
        if not ingredients and not named_ingredients:
            self.ingredients = ['Add ingredient']
        else:
            self.ingredients = ingredients
        self.named_ingredients = named_ingredients
        add_ingred_block = ur.Button('Add Ingredient Block',
                                        on_press=self._add_block)

        add_ingred_block = ur.GridFlow([add_ingred_block], 24, 0, 0, 'left')

        self.ingred_blocks = []
        self.ingred_blocks.append(add_ingred_block)
        if self.ingredients:
            self._add_block(self.ingredients)
        if self.named_ingredients:
            for item in self.named_ingredients:
                ingreds = self.named_ingredients[item]
                self._add_block(ingredients=ingreds, name=item)

    def _add_block(self, ingredients=[], name=None):
        if isinstance(ingredients, ur.Button):
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
        self.main_container = ur.Pile(self.ingred_blocks, focus_item=focus_item)
        super().__init__(self.main_container)

    @property
    def blocks(self):
        return self.ingred_blocks[1:]


class EntryBlock(ur.WidgetWrap):
    """Base class for stacked entry widgets."""
    def __init__(self, entries=[], wrap_amount=70):
        self.widgets = deque()
        wrapped = wrap(entries, wrap_amount)

        for index, item in wrapped:
            entry_widget = ur.Edit(str(index), item)
            self.widgets.append(entry_widget)
        self._refresh()

    def _refresh(self, focus_item=0):
        """Refresh the class to reflect changes to the entry stack."""
        self.entry_block = ur.Pile(self.widgets, focus_item=focus_item)
        super().__init__(self.entry_block)

    def keypress(self, size, key):
        """Capture and process a keypress."""
        key = super().keypress(size, key)
        self.row = self.entry_block.focus_position
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

    def add_entry(self, button=None):
        """Add an entry to the end of the list."""
        ingred_entry = ur.Edit("- ", '')
        self.widgets.append(ingred_entry)
        new_focus = len(self.widgets) - 1
        self._refresh(new_focus)

    def insert_entry(self, size, key):
        """Insert entry on next line and move cursor."""
        ingred_entry = ur.Edit("- ", '')
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
            if isinstance(widget, (ur.AttrMap, ur.Padding, ur.Columns)):
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
            if isinstance(item, ur.GridFlow):
                continue
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
            self.ingredients = ["add"]

        self.name = name
        self.widgets = deque([BLANK])
        buttons = self._get_buttons()
        self.widgets.append(buttons)
        if name:
            self.named_name = ur.AttrMap(ur.Edit('* ', name), 'title')
            self.widgets.append(self.named_name)
        
        for item in self.ingredients:
            ingred_entry = ur.Edit("- ", item)
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

    def delete_block(self, button):
        """Delete entire block of ingredients."""
        self.widgets.clear()
        del self.ingredients
        self.name = ''
        self._refresh()

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

    def del_entry(self, size, key):
        """Delete an entry."""
        widget = self.widgets[self.row]
        try:
            # We have an alt_name to account for
            assert isinstance(self.widgets[2], ur.AttrMap)
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
        named_ingreds = {}
        for item in self.widgets:
            if isinstance(item, ur.AttrMap):
                self.name = item.original_widget.get_edit_text()
            if isinstance(item, ur.Edit):
                ingredients.append(item.get_edit_text())

        if self.name:
            named_ingreds[self.name] = ingredients
            return named_ingreds
        else:
            return ingredients


class MethodBlock(EntryBlock):
    """Display an editable list of methods."""
    def __init__(self, method=[]):
        self.method = method
        if not self.method:
            self.method = ['Add method here.']
        super().__init__(self.method)
    
    def insert_entry(self, size, key):
        """Insert entry on next line and move cursor."""

        row_plus = self.row + 1
        ingred_entry = ur.Edit('- ', '')
        
        self.widgets.insert(row_plus, ingred_entry)
        self.entry_block.move_cursor_to_coords(size, 2, self.row)
        self._refresh(row_plus)

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
            if isinstance(item, ur.GridFlow):
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
    def __init__(self, recipe, recipe_yield=0, add=False):
        if add:
            # We are adding a new recipe. Init a recipe with no data
            self.recipe = Recipe()
            self.recipe.name = recipe
            self.recipe.uuid = str(uuid.uuid4())
            self.welcome = 'Add a Recipe: {}'.format(self.recipe.name)
        else:
            self.recipe = recipe
            self.welcome = 'Edit: {}'.format(self.recipe.name)
        #self.initial_state = Recipe(self.recipe.name)
        self.initial_state = copy.deepcopy(self.recipe)
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
            ur.AttrMap(ur.IntEdit('Bake Time: ', self.recipe.bake_time), 
                                  'bake_time'
                                  ),
            ur.AttrMap(ur.Edit('Oven Temp: ', 
                               self.recipe.oven_temp),'oven_temp'),
            ur.AttrMap(ur.Edit('Price($): ', self.recipe.price), 'price'),
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
        ingreds, named = self.recipe.get_ingredients(fmt='string')

        self.ingred_block = IngredientsContainer(
            ingredients=ingreds, named_ingredients=named
        )
        self.method_block = MethodBlock(
            self.recipe.method
        )
        self.notes_block = NoteBlock(
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
            raise ur.ExitMainLoop()
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
        else:
            pass

    @property
    def recipe_changed(self):
        """Check if the state of the recipe has changed."""
        changed = False
        self.update_recipe_data()
        if self.initial_state != self.recipe:
            changed = True
        return changed

    def get_recipe_name(self, name):
        """Check to see if name is already in database.

        If a recipe with the same name already exist in the database,
        this does a check and names the recipe with a number if it already
        exists in the database.
        """
        names = DBInfo().get_recipes()
        # case insensitive
        lower_name = name.lower()
        if lower_name != self.original_name.lower():
            if lower_name in names:
                i = 2
                new_name = '{} ({})'.format(name, i)
                while new_name in names:
                    new_name = '{} ({})'.format(name, i)
                    i += 1
                name = new_name

        return name

    def update_recipe_data(self):
        """Grab the data from the editors."""
        # gen info
        gen_info = self.general_info.original_widget.widget_list
        for item in gen_info:
            attr = item.attr_map[None]
            edit_text = item.original_widget.get_edit_text()
            if edit_text == '':
                del self.recipe[attr]
            else:
                # If the name is the same as another recipe
                # we name it 'recipe_name (2)' 3 4 ... etc
                if attr == 'name':
                    edit_text = self.get_recipe_name(edit_text)
                self.recipe[attr] = edit_text

        for item in self.disht_group:
            if item.get_state() == True:
                self.recipe.dish_type = item.get_label()

        # ingredients
        ingredients = []
        named_ingreds = []
        names = []
        for block in self.ingred_block.blocks:
            ingreds = block.get_ingredients()
            if isinstance(ingreds, dict):
                named_ingreds.append(ingreds)
                names += list(ingreds.keys())
            else:
                ingredients += ingreds

        if len(ingredients) > 0:
            self.recipe.ingredients = ingredients
        else:
            try:
                del self.recipe['ingredients']
            except KeyError:
                pass

        if len(named_ingreds) > 0:
            self.recipe.named_ingredients = named_ingreds
        else:
            try:
                del self.recipe.named_ingredients
            except KeyError:
                pass

        # method
        steps = []
        method_entries = self.method_block.get_entries()
        for item in method_entries:
            steps.append({'step': item})
        self.recipe.steps = steps

        # notes if any
        notes = self.notes_block.get_entries()
        if notes:
            self.recipe.notes = notes

    def save_recipe(self):
        """Save the current state of the recipe and exit."""
        self.update_recipe_data()
        raise ur.ExitMainLoop()

    def start(self):
        """Main entry point of the recipe editor."""
        self.loop = self.setup_view()
        self.loop.run()
        return self.recipe


if __name__ == '__main__':
    r = Recipe('test')
    r.print_recipe()
    #RecipeEditor(r).start()
    test = RecipeEditor(r)
