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
        cls.fi = open(os.devnull, 'w')
        sys.stdout = cls.fi
        sys.stderr = cls.fi
        
        parser = get_parser()
        cls.parser = parser

    @classmethod
    def tearDownClass(cls):
        cls.fi.close()
        


class RecipeTestCase(unittest.TestCase):
    #def setUp(self):
    #    self.recipe = Recipe()
    
    # print
    def itest_all_recipes(self):
        """User passes no args, and should be offered help."""
        for item in RECIPE_DATA_FILES:
            recipe = Recipe(item)
            with self.subTest():
                _dir = dir(recipe)
                self.assertIn('source', _dir)
                self.assertIn('uuid', _dir)
                self.assertIsInstance(recipe.ingredients, list)
                self.assertIsInstance(recipe.uuid, str)
                #self.assertIn('named_ingredients', dir(recipe))

class ComandsTestCase(CommandLineTestCase):
    def test_print_cmd(self):
        """User passes no args, and should be offered help."""
        subcmd = 'print'
        with self.subTest():
            arg = [subcmd]
            with self.assertRaises(SystemExit) as cm:
                parsed_args = self.parser.parse_args(arg)
                cmd_print(parsed_args)
            error = cm.exception.code
            self.assertEqual(error, 2)
            
            arg = [subcmd, '-h']
            with self.assertRaises(SystemExit) as cm:
                parsed_args = self.parser.parse_args(arg)
                cmd_print(parsed_args)
            error = cm.exception.code
            self.assertEqual(error, 0)
            
            arg = [subcmd, 'test']
            parsed_args = self.parser.parse_args(arg)
            cmd_print(parsed_args)
    
    def BAKtest_edit_cmd(self):
        """User passes no args, and should be offered help."""
        """I dont know how to implement this one yet."""
        subcmd = 'edit'
        args = [
            (subcmd, 'test'),
        ]
        for arg in args:
            with self.subTest():
                parsed_args = self.parser.parse_args(arg)
                cmd_edit(parsed_args)
    
    def test_shop_cmd(self):
        """User passes no args, and should be offered help."""
        subcmd = 'shop'
        args = [
            (subcmd, '-r'),
            (subcmd, '-r 2'),
        ]
        for arg in args:
            with self.subTest():
                parsed_args = self.parser.parse_args(arg)
                cmd_shop(parsed_args)

    def test_show_cmd(self):
        """Show the statistics of the recipe database."""
        subcmd = 'show'
        args = [
            (subcmd,),
        ]
        for arg in args:
            with self.subTest():
                parsed_args = self.parser.parse_args(arg)
                cmd_show(parsed_args)

if __name__ == "__main__":
    unittest.main()
