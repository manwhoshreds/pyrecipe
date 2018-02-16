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

from urwid import *
from birdseye import eye

from pyrecipe.config import (DISH_TYPES)
from pyrecipe.recipe import Recipe, IngredientParser
from pyrecipe.utils import wrap


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

HEADINGS = {
            'general_info': AttrMap(Text('General Information:'), 'heading'),
            'dish_types': AttrMap(Text('Dish Types:'), 'heading'),
            'testing': AttrMap(Text('Testing:'), 'heading'),
            'ingredients': AttrMap(Text('Ingredients:'), 'heading'),
            'method': AttrMap(Text('Method:'), 'heading'),
            }

BLANK = Divider()

class IngredBlock(WidgetWrap):

    def __init__(self, ingredients=[], alt_ingred=None):
        self.ingredients = ingredients
        self.alt_ingred = alt_ingred
        if not isinstance(self.ingredients, list):
            raise TypeError('IngredBlock only excepts a list of ingredients')
        
        self.widgets = deque()
        self.add_button = Button('Add Ingredient',
                    on_press=self.add_ingredient)
        self.add_button = Padding(self.add_button, 'left', right=8)
        
        self.add_name = Button('Toggle Name',
                    on_press=self.toggle_name)
        self.add_name = Padding(self.add_name, 'left', right=10)
        
        self.del_block = Button('Delete Block',
                    on_press=self.delete_block)
        self.del_block = Padding(self.del_block, 'left', right=8)
        self.buttons = Columns([self.add_button, 
                                    self.add_name,
                                    self.del_block
                                   ])
        
        if alt_ingred:
            self.alt_name = AttrMap(Edit('* ', alt_ingred), 'title')
            self.widgets.append(self.alt_name)
        
        if len(self.ingredients) < 1:
            ingred_entry = Edit("- ", 'add ingredient')
            self.widgets.append(ingred_entry)
        else:
            for item in self.ingredients:
                ingred_entry = Edit("- ", item)
                self.widgets.append(ingred_entry)
        self._refresh()

    #def __init__(self, ingredients=[], alt_ingred=None):
   #     self.blocks = deque()
   #     self.add_block(ingredients, alt_ingred)
    
    def _refresh(self, focus_item=0):
        self.ingred_edits = Pile(self.widgets, focus_item=focus_item)
        self.pile = Pile([self.buttons, self.ingred_edits], focus_item=focus_item)

        super().__init__(self.pile)
    
    def add_block(self, ingredients=[], alt_ingred=None):
        if not isinstance(ingredients, list):
            raise TypeError('IngredBlock only excepts a list of ingredients')
        
        self.widgets = deque()
        self.add_button = Button('Add Ingredient',
                    on_press=self.add_ingredient)
        self.add_button = Padding(self.add_button, 'left', right=8)
        
        self.add_name = Button('Toggle Name',
                    on_press=self.toggle_name)
        self.add_name = Padding(self.add_name, 'left', right=10)
        
        self.del_block = Button('Delete Block',
                    on_press=self.delete_block)
        self.del_block = Padding(self.del_block, 'left', right=8)
        self.buttons = Columns([self.add_button, 
                                self.add_name,
                                self.del_block
                                ])
        self.widgets.append(self.buttons)
        
        if alt_ingred:
            self.alt_name = AttrMap(Edit('* ', alt_ingred), 'title')
            self.widgets.append(self.alt_name)
        
        if len(ingredients) < 1:
            ingred_entry = Edit("- ", 'add ingredient')
            self.widgets.append(ingred_entry)
        else:
            for item in ingredients:
                ingred_entry = Edit("- ", item)
                self.widgets.append(ingred_entry)
        self._refresh()
    
    def delete_block(self, button):
        self.widgets.clear()
        del self.ingredients
        self.alt_ingred = ''
        self._refresh()

    def toggle_name(self, button):
        self.name = self.widgets[1]
        if not self.alt_ingred:
            self.alt_name = AttrMap(Edit('* ', 'Name'), 'title')
            self.widgets.insert(1, self.alt_name)
            self.alt_ingred = self.alt_name.original_widget.get_edit_text()
            self._refresh(1)
        else:
            for item in self.widgets:
                try:
                    if item.attr_map[None] == 'title':
                        self.widgets.remove(item)
                        self.alt_ingred = None
                        break
                except AttributeError:
                    pass
            self._refresh(1)

    def add_ingredient(self, button=None):
        ingred_entry = Edit("- ", '')
        self.widgets.append(ingred_entry)
        new_focus = len(self.widgets)
        self._refresh(focus_item=new_focus)

    def del_ingredient(self, size, key):
        widget = self.widgets[self.row]
        if isinstance(widget, (AttrMap, Padding, Columns)):
            return
        row_minus_one = self.row - 1
        row_minus_one = self.widgets[row_minus_one]
        if isinstance(row_minus_one, (AttrMap, Columns)):
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
        self._refresh(self.row)

    def move_entry(self, size, key):
        widget = self.widgets[self.row-1]
        if isinstance(widget, (AttrMap, Padding, Columns)):
            return
        try: 
            row = self.row
            col = len(self.widgets[row].edit_text) + 2
        except IndexError:
            row = self.row
            col = len(self.widgets[row].edit_text) - 2
        
        self.pile.move_cursor_to_coords(size, col, row)
        if key == 'f5':
            # up
            newfocus = self.row - 1
        else:
            # down
            newfocus = self.row + 1

        item = list(self.widgets)[self.row]
        self.widgets.remove(item)
        self.widgets.insert(newfocus, item)
        self._refresh(newfocus)
    
    def keypress(self, size, key):
        key = super().keypress(size, key)
        self.row = self.ingred_edits.focus_position
        self.end_col = len(self.widgets[self.row].edit_text) + 2
        pressed = {
                'enter': self.on_enter,
                'ctrl d': self.del_ingredient,
                'f5': self.move_entry,
                'f6': self.move_entry,
                'f9': self._test
                }
        try:
            # I only need to pass key to one function
            # unfortunately i will have to pass to all
            # this is still a verly clean way to write the code
            # as opossed to the if, elif, etc....
            # perhaps a better way eludes me
            pressed[key](size, key)
        except KeyError:
            return key

    def _test(self, size, key):
        self._refresh

    def on_enter(self, size, key):
        try:
            self.ingred_edits.set_focus(self.row + 1)
        except IndexError:
            pass

    def is_not_entry(self, focus):
        widget = self.widgets[focus]
        if isinstance(widget, (AttrMap, Padding, Columns)):
            return True
        else:
            return False
    
    def get_ingredients(self):
        ingredients = []
        alt_ingreds = {}
        for item in self.widgets:
            if isinstance(item, Edit):
                    ingredients.append(item.get_edit_text())
        
        if self.alt_ingred:
            alt_ingreds[self.alt_ingred] = ingredients
            return alt_ingreds
        else:
            return ingredients

class MethodBlock(WidgetWrap):

    def __init__(self, method=[]):
        self.method_widgets = deque()
        self.method = method
        if not isinstance(self.method, list):
            raise TypeError('MethodBlock only excepts a list of methods')
        
        add_button = Button('Add Method',
                on_press=self.add_method)
        self.method_widgets.append(GridFlow([add_button], 14, 0, 0, 'left'))
        
        wrapped = wrap(self.method)
        for index, item in wrapped:
            method_entry = Edit(str(index) + ' ', item)
            self.method_widgets.append(method_entry)
            
        if len(self.method_widgets) > 0:
            method_pile = Pile(self.method_widgets)
        else:
            method_pile = BLANK
        self._refresh()

    def _refresh(self, focus_item=1):
        try:
            self.pile = Pile(self.method_widgets, focus_item=focus_item)
        except IndexError:
            self.pile = Pile(self.method_widgets, focus_item=focus_item-1)
        self.num_widgets = len(self.method_widgets)
        super().__init__(self.pile)
    
    def _renumber(self, focus_item=1):
        self.method_widgets.clear()
        wrapped = wrap(self.method)
        for index, item in wrapped:
            method_entry = Edit(str(index) + ' ', item)
            self.method_widgets.append(method_entry)
        try:
            self.pile = Pile(self.method_widgets, focus_item=focus_item)
        except IndexError:
            self.pile = Pile(self.method_widgets, focus_item=focus_item-1)
        self.num_widgets = len(self.method_widgets)
        super().__init__(self.pile)

    def add_method(self, button):
        caption = str(len(self.method_widgets))
        method_entry = Edit(caption + ". ", '')
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
        #self._refresh(self.focus_pos)
        self._renumber(self.focus_pos)

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

class RecipeEditor:
    
    footer_text = ('foot', [
        ('pyrecipe', ' PYRECIPE    '),
        ('key', "F2"), ('footer', ' Save  '),
        ('key', "Esc"), ('footer', ' Quit  '),
        ('key', "F5/F6"), ('footer', ' Move item UP/DOWN  '),
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

        self.general_info = [AttrMap(Edit('Enter recipe name: ', self.r['recipe_name']), 'recipe_name'),
                             AttrMap(IntEdit('Enter prep time: ', self.r['prep_time']), 'prep_time'),
                             AttrMap(IntEdit('Enter cook time: ', self.r['cook_time']), 'cook_time'),
                             AttrMap(IntEdit('Enter bake time: ', self.r['bake_time']), 'bake_time'),
                             AttrMap(Edit('Enter price($): ', self.r['price']), 'price'),
                             AttrMap(Edit('Enter source url: ', self.r['source_url'], wrap='clip'), 'source_url'),
                             AttrMap(Edit('Enter author: ', self.r['author']), 'author')]

        self.general_info = Padding(Pile(self.general_info), align='left', left=2)
        
        headings_general_and_dish_types = GridFlow(
                    [HEADINGS['general_info'], 
                     HEADINGS['dish_types'],
                     HEADINGS['testing']
                     ], 53, 0, 2, 'left'
                )
        headings_ingred_and_method = GridFlow(
                    [HEADINGS['ingredients'], 
                     HEADINGS['method'],
                     ], 79, 0, 2, 'left'
                )
        self.ingred_blocks = []
        self.ingred_blocks.append(IngredBlock(self.r.get_ingredients()))
        #self.ingred_block.add_block(self.r.get_ingredients())
        
        if self.r.has_alt_ingredients: 
            for item in self.r.alt_ingreds:
                self.ingred_blocks.append(BLANK)
                self.ingred_block = self.ingred_blocks.append(IngredBlock(self.r.get_ingredients(alt_ingred=item), alt_ingred=item))
        
        self.method_block = MethodBlock(self.r.get_method())
        
        test = Padding(Button('hello', self._testing), 'left', ('relative', 20))
        general_and_dish = GridFlow([self.general_info, radio_dish_types, test], 53, 0, 2, 'left')
        ingred_and_method = GridFlow([Pile(self.ingred_blocks), self.method_block], 79, 0, 2, 'left')
        
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
        
        list_box = ListBox(SimpleListWalker(self.listbox_content))
        
        return list_box
    
    def handle_input(self, key):
        if key in ('f8', 'esc'):
            raise ExitMainLoop()
        elif key in ('f2',):
            self.save_recipe()
        elif key in ('f9',):
            self._testing(key)
        else:
            pass

    def save_recipe(self):
        # gen info
        gen_info = self.general_info.original_widget.widget_list
        for item in gen_info:
            attr = item.attr_map[None]
            edit_text = item.original_widget.get_edit_text()
            print(edit_text)
            if edit_text != '':
                self.r[attr] = edit_text
         
        for item in self.disht_group:
            if item.get_state() == True:
                self.r['dish_type'] = item.get_label()
        
        # ingredients
        ingredients = []
        alt_ingredients = []
        alt_names = []
        for item in self.ingred_blocks:
            if isinstance(item, Divider):
                continue
            elif not item.alt_ingred:
                ingreds = item.get_ingredients()
                for item in ingreds:
                    parsed = ingred_parser.parse(item)
                    ingredients.append(parsed)
            else:
                alt_names.append(item.alt_ingred)
                ingreds = item.get_ingredients()
                ingreds = ingreds[item.alt_ingred]
                ingred_list = []
                ingred_dict = {}
                for ingred in list(ingreds):
                    parsed = ingred_parser.parse(ingred)
                    ingred_list.append(parsed)
                ingred_dict[item.alt_ingred] = ingred_list
                alt_ingredients.append(ingred_dict)


        self.r['ingredients'] = ingredients
        if len(alt_ingredients) > 0:
            self.r['alt_ingreds'] = alt_names
            self.r['alt_ingredients'] = alt_ingredients
        else:
            self.r['alt_ingreds'] = None
        print(alt_ingredients) 
        # method
        steps = []
        for item in self.method_block.method_widgets:
            if isinstance(item, GridFlow):
                continue
            pre_processed = item.get_edit_text()
            step = ' '.join(pre_processed.split())
            steps.append({'step': step})
        
        self.r['steps'] = steps
        # save the recipe
        if self.add:
            self.r.save(save_as=True)
        else:
            self.r.save()
        raise ExitMainLoop()

    def _testing(self, button):
        self.ingred_blocks.append(IngredBlock(['hello']))
        self.loop = self.setup_view()
    
    def start(self):
        self.loop = self.setup_view()
        self.loop.run()
        

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
    
    RecipeEditor('pesto').start()
    #test = AttrMap(Edit('enter stuff', 'hell'), 'hell')
