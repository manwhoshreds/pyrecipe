import os
import sys
import unittest
from io import StringIO

from pyrecipe.__main__ import *
from pyrecipe.recipe import Recipe
from pyrecipe.shopper import ShoppingList
from pyrecipe.config import RECIPE_DATA_FILES

class CommandLineTestCase(unittest.TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    @classmethod
    def setUpClass(cls):
        # supress output
        #cls.fi = open(os.devnull, 'w')
        #sys.stdout = cls.fi
        #sys.stderr = cls.fi
        
        parser = get_parser()
        cls.parser = parser

    @classmethod
    def tearDownClass(cls):
        pass
        #cls.fi.close()
        


class RecipeTestCase(unittest.TestCase):
    def itest_all_recipes(self):
        """User passes no args, and should be offered help."""
        for item in RECIPE_DATA_FILES:
            recipe = Recipe(item)
            shoplist = ShoppingList()
            shoplist.update(recipe)
            shoplist.print_list()
            print(recipe.name)
            with self.subTest(i=item):
                _dir = dir(recipe)
                self.assertIn('source', _dir)
                self.assertIn('uuid', _dir)
                self.assertIsInstance(recipe.ingredients, list)
                self.assertIsInstance(recipe.uuid, str)
                #self.assertIn('named_ingredients', dir(recipe))

class PrintCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'print'
        self.cmd = cmd_print
    
    def test_print_without_args(self):
        """recipe_tool print"""
        arg = [self.subcmd]
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        error = cm.exception.code
        self.assertEqual(error, 2)
            
    def test_print_help(self):
        """recipe_tool print -h"""
        arg = [self.subcmd, '-h']
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        error = cm.exception.code
        self.assertEqual(error, 0)
            
    def test_print_recipe_from_file(self):
        """recipe_tool print test"""
        arg = [self.subcmd, 'test']
        parsed_args = self.parser.parse_args(arg)
        self.cmd(parsed_args)
            
    def test_print_recipe_from_web(self):
        """recipe_tool print <recipe from website>"""
        url = 'https://tasty.co/recipe/honey-roasted-bbq-pork-char-siu'
        arg = [self.subcmd, url]
        parsed_args = self.parser.parse_args(arg)
        self.cmd(parsed_args)

class ShopCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'shop'
        self.cmd = cmd_shop
        
    def test_shop_without_args(self):
        """recipe_tool shop"""
        arg = [self.subcmd]
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        # This one returns the exception str instead of a number
        error = cm.exception.code
        self.assertIsInstance(error, str)
            
    def test_shop_help(self):
        """recipe_tool shop -h"""
        arg = [self.subcmd, '-h']
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        error = cm.exception.code
        self.assertEqual(error, 0)
    
    def test_shop_with_random(self):
        """recipe_tool shop -r [NUM]."""
        args = [
            (self.subcmd, '-r'),
            (self.subcmd, '-r 2'),
        ]
        for arg in args:
            with self.subTest():
                parsed_args = self.parser.parse_args(arg)
                self.cmd(parsed_args)
    
    def test_shop_with_recipe(self):
        """recipe_tool shop <recipe>.{}"""
        arg = [self.subcmd, 'test']
        parsed_args = self.parser.parse_args(arg)
        self.cmd(parsed_args)

class ShowCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'show'
        self.cmd = cmd_show
    
    def test_show_cmd(self):
        """recipe_tool show"""
        arg = [self.subcmd]
        parsed_args = self.parser.parse_args(arg)
        self.cmd(parsed_args)

if __name__ == "__main__":
    unittest.main()
