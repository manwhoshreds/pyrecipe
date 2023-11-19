import os
import sys
import unittest

from pyrecipe.__main__ import *
from pyrecipe.backend.recipe import Recipe, Ingredient
from pyrecipe import CULINARY_UNITS
#from pyrecipe.config import RECIPE_DATA_FILES

skip = unittest.skip

class CommandLineTestCase(unittest.TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    @classmethod
    def setUpClass(cls):
        cls.dev_null = open(os.devnull, 'w')
        sys.stdout = cls.dev_null
        
        parser = get_parser()
        cls.parser = parser
        cls.units = CULINARY_UNITS

    @classmethod
    def tearDownClass(cls):
        cls.dev_null.close()

#@skip('because')
class RecipeTestCase(CommandLineTestCase):
    def test_all_recipes(self):
        """Validate every recipe file."""
        for item in RECIPE_DATA_FILES:
            recipe = Recipe(item)
            with self.subTest(i=recipe.name):
                _dir = dir(recipe)
                self.assertIn('source', _dir)
                self.assertIn('uuid', _dir)
                self.assertIsInstance(recipe.ingredients, list)
                self.assertIsInstance(recipe.uuid, str)

    def test_all_recipe_ingredients(self):
        """Validate every ingredient."""
        for item in RECIPE_DATA_FILES:
            recipe = Recipe(item)
            ingreds, named = recipe.get_ingredients(fmt='object')
            for item in ingreds:
                with self.subTest(i=recipe.name):
                    self.assertIn(item.unit, self.units)
            for item in named:
                for ingred in named[item]:
                    with self.subTest(i=recipe.name):
                        self.assertIn(ingred.unit, self.units)
            


#@skip('because')
class PrintCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'print'
        self.cmd = read_recipe

    def test_print_without_args(self):
        """recipe_tool print"""
        sys.stderr = self.dev_null
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
        for item in RECIPE_DATA_FILES:
            recipe = Recipe(item)
            with self.subTest(i=recipe.name):
                arg = [self.subcmd, recipe.name]
                parsed_args = self.parser.parse_args(arg)
                self.cmd(parsed_args)

    def test_print_recipe_from_file_with_verbose_flag(self):
        """recipe_tool -v print test"""
        for item in RECIPE_DATA_FILES:
            recipe = Recipe(item)
            with self.subTest(i=recipe.name):
                arg = ['-v', self.subcmd, recipe.name]
                parsed_args = self.parser.parse_args(arg)
                self.cmd(parsed_args)
    
    def test_print_recipe_from_web(self):
        """recipe_tool print <recipe from website>"""
        url = 'https://tasty.co/recipe/honey-roasted-bbq-pork-char-siu'
        arg = [self.subcmd, url]
        parsed_args = self.parser.parse_args(arg)
        self.cmd(parsed_args)


#@skip('because')
class EditCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'edit'
        self.cmd = cmd_edit


#@skip('because')
class AddCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'add'
        self.cmd = cmd_add


#@skip('because')
class RemoveCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'remove'
        self.cmd = cmd_remove

#@skip('because')
class SearchCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'search'
        self.cmd = cmd_search

    def itest_search_term_not_found(self):
        """recipe_tool search <not found>"""
        arg = [self.subcmd, "iknowthiswillneverreturnasearch"]
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        error = cm.exception.code
        self.assertEqual(error, 1)

    def test_search_term_found(self):
        """recipe_tool search <found>"""
        arg = [self.subcmd, "test"]
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        error = cm.exception.code
        self.assertIsInstance(error, str)


#@skip('because')
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


class DumpCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'dump'
        self.cmd = cmd_dump

    def test_dump_json(self):
        """recipe_tool dump -j test"""
        for item in RECIPE_DATA_FILES:
            recipe = Recipe(item)
            with self.subTest(i=recipe.name):
                arg = [self.subcmd, '-j', recipe.name]
                with self.assertRaises(SystemExit) as cm:
                    parsed_args = self.parser.parse_args(arg)
                    self.cmd(parsed_args)
            # exit with 0
            error = cm.exception.code
            self.assertIsNone(error)

    def test_dump_yaml(self):
        """recipe_tool dump -y test"""
        arg = [self.subcmd, '-y', 'test']
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        # exit with 0
        error = cm.exception.code
        self.assertIsNone(error)
    
    def test_dump_xml(self):
        """recipe_tool dump -x <recipe>"""
        arg = [self.subcmd, '-x', 'test']
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        # exit with 0
        error = cm.exception.code
        self.assertIsNone(error)

if __name__ == "__main__":
    unittest.main()
