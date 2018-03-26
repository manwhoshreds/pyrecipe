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
import time

import urwid
import speech_recognition as sr

from pyrecipe.config import (DISH_TYPES)
from pyrecipe.recipe import Recipe, IngredientParser
from pyrecipe.utils import wrap


ingred_parser = IngredientParser()

PALETTE = ([
    ('header', 'white', 'black', 'bold'),
    ('footer', 'white', 'black', 'bold'),
    ('foot', 'white', 'black', 'bold'),
    ('heading', 'dark cyan', 'black'),
    ('current_focus', 'dark cyan', 'black', 'bold'),
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

def get_speech():
    """Get speech from google."""
    r = sr.Recognizer()
    text = '' 
    while text != 'start recipe tool':
        with sr.Microphone(device_index=6) as source:
            try:
                r.adjust_for_ambient_noise(source)
                print('say something')
                audio = r.listen(source)
                text = r.recognize_google(audio)

                if text == "next ingredient":
                    print('Going to next ingredient')
                else:
                    print('{} is pretty cool but its not the response'
                          ' we were looking for'.format(text))
            except sr.UnknownValueError:
                print('I could not understand you sir')


class IngredBlock(urwid.WidgetWrap):
    """Ingredient block for displaying editable ingredients."""
    def __init__(self, ingredients=[], name=None):
        self.ingredients = ingredients
        self.name = name
        if not isinstance(self.ingredients, list):
            raise TypeError('IngredBlock only excepts a list of ingredients')
        
        self.widgets = deque([BLANK])
        if name:
            self.alt_name = urwid.AttrMap(urwid.Text('* {}'.format(name)), 'title')
            self.widgets.append(self.alt_name)
       
        current_focus = 0
        for index, item in enumerate(self.ingredients):
            if index == current_focus:
                ingred_entry = urwid.AttrMap(urwid.Text("- {}".format(item)), 'current_focus')
            else:
                ingred_entry = urwid.Text("- {}".format(item))
            self.widgets.append(ingred_entry)
        
        self._refresh()

    def _refresh(self, focus_item=1):
        self.ingred_block = urwid.Pile(self.widgets, focus_item=focus_item)
        super().__init__(self.ingred_block)
    
    def cur_focus_up(self, index):
        for item in self.widgets:
            if item.attr_map[None] == 'current_focus':
                self.widgets.append(urwid.Text("test"))

        self.widgets.append(urwid.Text("- test"))
        self._refresh()

    def keypress(self, size, key):
        key = super().keypress(size, key)
        self.row = self.ingred_block.focus
        print(self.row)
        try: 
            self.end_col = len(self.widgets[self.row].edit_text) + 2
            print(self.end_col)
        except:
            return key
        print(key) 
        pressed = {
                'enter': self.cur_focus_up
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
    
    def on_enter(self, size, key):
        try:
            col = len(self.widgets[self.row + 1].edit_text) + 2
            self.ingred_block.move_cursor_to_coords(size, col, self.row + 1)
        except IndexError:
            self.ingred_block.move_cursor_to_coords(size, 2, self.row)
            self.add_ingredient()

class EntryBlock(urwid.WidgetWrap):
    """Base class for entry piles."""
    def __init__(self, entries=[], wrap_amount=70):
        self.widgets = deque()
        if not isinstance(entries, list):
            raise TypeError('{} only excepts a list of methods'.format(__class__))
        
        wrapped = wrap(entries, wrap_amount)
        for index, item in wrapped:
            method_entry = urwid.Text('{} {}'.format(str(index), item))
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


class RecipeMaker:
    """The pyrecipe console interface for managing recipes."""
    footer_text = ('foot', [
        ('pyrecipe', ' PYRECIPE    '),
        ('key', "Esc"), ('footer', ' Quit  '),
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

        self.general_info = [
                    urwid.Text('Recipe Name: {}'.format(self.r['recipe_name'])),
                    urwid.Text('Dish Type: {}'.format(self.r['dish_type'])),
                    urwid.Text('Prep Time: {}'.format(self.r['prep_time'])),
                    urwid.Text('Cook Time: {}'.format(self.r['cook_time'])),
                    urwid.Text('Bake Time: {}'.format(self.r['bake_time'])),
                    urwid.Text('Price($): {}'.format(self.r['price'])),
                    urwid.Text('Source URL: {}'.format(self.r['source_url'])),
                    urwid.Text('Author: {}'.format(self.r['author'])),
                    #urwid.Text('Categories {}', self.r['categories']), 'categories')]
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
        self.ingred_block = IngredBlock(ingredients=ingreds) 
        self.method_block = MethodBlock(self.r.get_method())
        self.notes_block = NoteBlock(self.r['notes'])
        
        general_and_dish = urwid.GridFlow([self.general_info, self.notes_block], 53, 0, 2, 'left')
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
        text = "Are you sure you want to exit recipe maker?"
        question = urwid.Text(("bold", text), "center")
        
        cancel_btn = urwid.AttrMap(urwid.Button(
            "Cancel", self.prompt_answer, "cancel"), "title", None)
        quit_btn = urwid.AttrMap(urwid.Button(
            "Quit", self.prompt_answer, "quit"), "red", None)

        prompt = urwid.LineBox(urwid.ListBox(urwid.SimpleFocusListWalker(
            [question, BLANK, BLANK, cancel_btn, quit_btn])))
        
        overlay = urwid.Overlay(
            prompt, self.loop.widget,
            "center", 19, "middle", 9,
            16, 8)
        
        self.loop.widget = overlay 
    
    def prompt_answer(self, button, label):
        """Prompt answer"""
        if label == 'quit':
            raise urwid.ExitMainLoop()
        else:
            self.loop.widget = self.frame

    def handle_input(self, key):
        """Handle the input."""
        if key in ('f8', 'esc'):
            self.quit_prompt()
    
    def start(self):
        """Main entry point of the recipe editor."""
        self.loop = self.setup_view()
        self.loop.run()
        

if __name__ == '__main__':
    #get_speech()
    #time.sleep(4)
    RecipeMaker('test').start()
