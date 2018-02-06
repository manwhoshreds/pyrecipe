# -*- coding: utf-8 -*-
"""
    pyrecipe.console_gui.add_recipe
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A console gui built with urwid used to add recipes to pyrecipe

    :copyright: 2017 by Michael Miller
    :license: GPL, see LICENSE for more details.
"""
import textwrap

from urwid import *

from pyrecipe.config import (DISH_TYPES)
from pyrecipe.recipe import Recipe, IngredientParser


ingred_parser = IngredientParser(return_dict=True)

PALETTE = ([
    ('header', 'white', 'black', 'bold'),
    ('footer', 'white', 'black', 'bold'),
    ('foot', 'white', 'black', 'bold'),
    ('heading', 'dark cyan', 'black'),
    ('key', 'light cyan', 'black'),
    ('title', 'light cyan', 'default'),
    ('pyrecipe', 'light green', 'black'),
    ('button', 'yellow', 'dark green', 'standout'),
    ])

HEADINGS  = {
            'general_info': AttrMap(Text('General Information:'), 'heading'),
            'dish_types': AttrMap(Text('Dish Types:'), 'heading'),
            'ingredients': AttrMap(Text('Ingredients:'), 'heading'),
            'method': AttrMap(Text('Method:'), 'heading'),
            }

BLANK = Divider()

class IngredBlock(WidgetWrap):

    def __init__(self, ingredients=[], alt_ingred=None):
        self.ingred_widgets = []
        self.ingredients = ingredients
        if not isinstance(self.ingredients, list):
            raise TypeError('IngredBlock only excepts a list of ingredients')
        add_button = Button('Add Ingredient',
                on_press=self.add_ingredient)
        self.ingred_widgets.append(GridFlow([add_button], 18, 0, 0, 'left'))

        if len(self.ingredients) < 1:
            ingred_entry = Edit("- ", 'add ingredient')
            self.ingred_widgets.append(ingred_entry)
        else:
            for item in self.ingredients:
                ingred_entry = Edit("- ", item)
                self.ingred_widgets.append(ingred_entry)
        self._after_init()

    def _after_init(self, focus_item=1):
        try:
            self.pile = Pile(self.ingred_widgets, focus_item=focus_item)
        except IndexError:
            self.pile = Pile(self.ingred_widgets, focus_item=focus_item-1)
        self.num_widgets = len(self.ingred_widgets)
        super().__init__(self.pile)

    def add_ingredient(self, key):
        ingred_entry = Edit("- ", 'Add')
        self.ingred_widgets.append(ingred_entry)
        new_focus = len(self.ingred_widgets) - 1
        self._after_init(focus_item=new_focus)

    def del_ingredient(self, size):
        # dont let the user delete the add button at pos 0
        if self.focus_pos == 0:
            return
        if self.num_widgets == 2:
            self.ingred_widgets[1].edit_text = 'add ingred'
            return
        try: 
            row = self.focus_pos + 1
            col = len(self.ingred_widgets[row].edit_text) + 2
        except IndexError:
            row = self.focus_pos - 1
            col = len(self.ingred_widgets[row].edit_text) + 2

        self.pile.move_cursor_to_coords(size, col, row)
        try: 
            self.ingred_widgets.pop(self.focus_pos)
        except IndexError:
            pass
        self._after_init(self.focus_pos)

    def keypress(self, size, key):
        self.focus_pos = self.pile.focus_position
        key = super().keypress(size, key)
        if key == 'enter':
            self.on_enter(key)
        elif key == 'ctrl d':
            self.del_ingredient(size)
        else:
            return key

    def on_enter(self, key):
        try:
            self.pile.set_focus(self.focus_pos + 1)
        except IndexError:
            pass


class MethodBlock(WidgetWrap):

    def __init__(self, method=[]):
        self.method_widgets = []
        self.method = method
        if not isinstance(self.method, list):
            raise TypeError('MethodBlock only excepts a list of methods')
        
        add_button = Button('Add Method',
                on_press=self.add_method)
        self.method_widgets.append(add_button)
        
        wrapper = textwrap.TextWrapper(width=70)
        if len(self.method) > 9:
            wrapper.initial_indent = ' '
            wrapper.subsequent_indent = '    '
        else:
            wrapper.subsequent_indent = '   '

        for index, step in enumerate(self.method, start=1):
            if index >= 10:
                wrapper.initial_indent = ''
                wrapper.subsequent_indent = '    '
            wrap = wrapper.fill(step)
            method_entry = AttrMap(Edit(str(index) + ". ", wrap), 'entry')
            self.method_widgets.append(method_entry)
            
        if len(self.method_widgets) > 0:
            method_pile = Pile(self.method_widgets)
        else:
            method_pile = BLANK
        
        if len(self.method) < 1:
            method_entry = AttrMap(Edit("- ", 'add method'), 'entry')
            self.method_widgets.append(method_entry)
        else:
            for item in self.method:
                method_entry = AttrMap(Edit("- ", item), 'entry')
                self.method_widgets.append(method_entry)
        self._after_init()

    def _after_init(self):
        self.pile = Pile(self.method_widgets)
        self.pile.set_focus(1)
        super().__init__(self.pile)

    def add_method(self, key):
        method_entry = AttrMap(Edit("- ", 'Add'), 'entry')
        self.method_widgets.append(method_entry)
        self._after_init()


class RecipeEditor:
    
    footer_text = ('foot', [
        ('pyrecipe', ' PYRECIPE    '),
        ('key', "F2"), ('footer', ' save  '),
        ('key', "Esc"), ('footer', ' quit  '),
        ('key', "Ctrl-d"), ('footer', ' del ingredient/method  ')
        ])

    def __init__(self, recipe=''):
        self.r = Recipe(recipe)
        if self.r['recipe_name']:
            self.welcome = 'Edit: {}'.format(self.r['recipe_name'])
        else:
            self.welcome = 'Add a Recipe'
        
        self.gernal_info = []
        self.disht_group = []
        self.ingred_widgets = []
        self.alt_ingred_widgets = []
        self.method_widgets = []

    def setup_view(self):
        header = AttrMap(Text(self.welcome), 'header')
        listbox = self.setup_listbox()
        frame = Frame(AttrMap(listbox, 'body'), header=header)
        frame.footer = AttrMap(Text(
            self.footer_text), 'footer')
        loop = MainLoop(frame, palette=PALETTE)
        loop.unhandled_input = self.handle_input
        loop.pop_ups = True
        return loop
    
    def setup_listbox(self):
    
        radio_dish_types = Pile([AttrMap(RadioButton(self.disht_group,
                            txt), 'buttn', 'buttnf')
                            for txt in DISH_TYPES])

        for item in self.disht_group:
            if item.get_label() == self.r['dish_type']:
                item.set_state(True)

        alt_ingred_widgets = []
        if self.r['alt_ingreds']:
            for item in self.r['alt_ingreds']:
                alt_ingred_widgets.append(BLANK)
                alt_ingred_widgets.append(AttrMap(Text(item), 'title'))
                for ingred in self.r.get_ingredients(alt_ingred=item):
                    this = AttrMap(Edit("- ", ingred), 'entry')
                    alt_ingred_widgets.append(this)

        if len(self.ingred_widgets) or len(alt_ingred_widgets) > 1:
            ingred_pile = Padding(Pile(self.ingred_widgets + alt_ingred_widgets), align='left', left=2)
        else:
            ingred_pile = BLANK

        wrapper = textwrap.TextWrapper(width=70)
        if len(self.r['steps']) > 9:
            wrapper.initial_indent = ' '
            wrapper.subsequent_indent = '    '
        else:
            wrapper.subsequent_indent = '   '

        for index, step in enumerate(self.r['steps'], start=1):
            if index >= 10:
                wrapper.initial_indent = ''
                wrapper.subsequent_indent = '    '
            wrap = wrapper.fill(step['step'])
            method_entry = AttrMap(Edit(str(index) + ". ", wrap), 'entry')
            self.method_widgets.append(method_entry)
            
        if len(self.method_widgets) > 0:
            method_pile = Pile(self.method_widgets)
        else:
            method_pile = BLANK

        self.general_info = [AttrMap(Edit('Enter recipe name: ', self.r['recipe_name']), 'recipe_name'),
                             AttrMap(IntEdit('Enter prep time: ', self.r['prep_time']), 'prep_time'),
                             AttrMap(IntEdit('Enter cook time: ', self.r['cook_time']), 'cook_time'),
                             AttrMap(IntEdit('Enter bake time: ', self.r['bake_time']), 'bake_time'),
                             AttrMap(Edit('Enter price: ', self.r['price']), 'price'),
                             AttrMap(Edit('Enter source url: ', self.r['source_url'], wrap='clip'), 'source_url'),
                             AttrMap(Edit('Enter author: ', self.r['author']), 'author')]

        general_pile = Padding(Pile(self.general_info), align='left', left=2)
        headings_general_and_dish_types = GridFlow(
                    [HEADINGS['general_info'], HEADINGS['dish_types']], 79, 0, 2, 'left'
                )
        headings_ingred_and_method = GridFlow(
                    [HEADINGS['ingredients'], HEADINGS['method']], 79, 0, 2, 'left'
                )
        self.ingred_block = IngredBlock(self.r.get_ingredients())
        ingred_and_method = GridFlow([self.ingred_block, method_pile], 79, 0, 2, 'left')
        general_and_dish = GridFlow([general_pile, radio_dish_types], 79, 0, 2, 'left')
        
        listbox_content = [
                BLANK,
                headings_general_and_dish_types,
                BLANK,
                general_and_dish,
                BLANK,
                headings_ingred_and_method,
                BLANK,
                ingred_and_method
                ]
        
        list_box = ListBox(SimpleListWalker(listbox_content))
        
        return list_box
    
    def handle_input(self, key):
        if key in ('f8', 'esc'):
            raise ExitMainLoop()
        elif key in ('f2',):
            self.save_recipe()
        else:
            pass

    def save_recipe(self):
        for item in self.general_info:
            attr = item.attr_map[None]
            edit_text = item.original_widget.get_edit_text()
            self.r[attr] = edit_text
            
        for item in self.disht_group:
            if item.get_state() == True:
                self.r['dish_type'] = item.get_label()
        
        ingredients = []
        for item in self.ingred_block.ingred_widgets:
            if isinstance(item, Button):
                continue
            ingred = item.original_widget.get_edit_text()
            ingred_dict = ingred_parser.parse(ingred)
            ingredients.append(ingred_dict)
            
        self.r['ingredients'] = ingredients
        
        steps = []
        for item in self.method_widgets:
            pre_processed = item.original_widget.get_edit_text()
            step = ' '.join(pre_processed.split())
            steps.append({'step': step})

        self.r['steps'] = steps
        print(self.r)
        # save the recipe
        #self.r.save_state()
        #raise ExitMainLoop()

    def start(self):
        loop = self.setup_view()
        loop.run()

class PopUpDialog(WidgetWrap):
    """A dialog that appears with nothing but a close button """
    signals = ['close']
    def __init__(self):
        close_button = Button("that's pretty cool")
        connect_signal(close_button, 'click',
            lambda button:self._emit("close"))
        pile = Pile([Text(
            "^^  I'm attached to the widget that opened me. "
            "Try resizing the window!\n"), close_button])
        fill = Filler(pile)
        self.__super.__init__(AttrMap(fill, 'popbg'))


class ThingWithAPopUp(PopUpLauncher):
    def __init__(self):
        self.__super.__init__(Button("click-me"))
        connect_signal(self.original_widget, 'click',
            lambda button: self.open_pop_up())

    def create_pop_up(self):
        pop_up = PopUpDialog()
        connect_signal(pop_up, 'close',
            lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left':0, 'top':1, 'overlay_width':32, 'overlay_height':7}


if __name__ == '__main__':
    
    RecipeEditor('7 cheese mac and cheese').start()
    #test = AttrMap(Edit('enter stuff', 'hell'), 'hell')
    #print(test.original_widget.get_edit_text())
    #r = Recipe('7 cheese mac and cheese')

    #fill = Filler(IngredBlock(r.get_ingredients()), 'top')
    #fill = Filler(IngredBlock())
    #loop = MainLoop(
    #    fill,
    #    [('popbg', 'white', 'dark blue')])
    #loop.run()

