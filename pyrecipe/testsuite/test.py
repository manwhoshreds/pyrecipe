import os
import sys
import unittest

from pyrecipe.__main__ import *
from pyrecipe.recipe import Recipe, Ingredient
from pyrecipe import CULINARY_UNITS
from pyrecipe.shopper import ShoppingList
from pyrecipe.config import RECIPE_DATA_FILES

class CommandLineTestCase(unittest.TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    @classmethod
    def setUpClass(cls):
        cls.f = open(os.devnull, 'w')
        sys.stderr = cls.f
    #    sys.stdout = cls.f
        
        parser = get_parser()
        cls.parser = parser
        cls.units = CULINARY_UNITS

    @classmethod
    def tearDownClass(cls):
        cls.f.close()

class RecipeTestCase:#(CommandLineTestCase):
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
            ingreds, named = recipe.get_ingredients(fmt='data')
            for item in ingreds:
                with self.subTest(i=recipe.name):
                    self.assertIn(item.unit, self.units)
            for item in named:
                for ingred in named[item]:
                    with self.subTest(i=recipe.name):
                        self.assertIn(ingred.unit, self.units)



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


class EditCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'edit'
        self.cmd = cmd_edit


class EditCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'add'
        self.cmd = cmd_add


class RemoveCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'remove'
        self.cmd = cmd_remove


class MakeCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'make'
        self.cmd = cmd_make

class SearchCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'search'
        self.cmd = cmd_search

    def test_search_term_not_found(self):
        """recipe_tool search <not found>"""
        arg = [self.subcmd, "iknowthiswillneverreturnasearch"]
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        error = cm.exception.code
        self.assertEqual(error, 1)

    def test_search_term_not_found(self):
        """recipe_tool search <found>"""
        arg = [self.subcmd, "test"]
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        error = cm.exception.code
        self.assertIsInstance(error, str)

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
        """recipe_tool dump -j <recipe>"""
        arg = [self.subcmd, '-j', 'test']
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        print(dir(cm.exception.code))
        error = cm.exception.code
        self.assertEqual(error, 1)

    def itest_dump_yaml(self):
        """recipe_tool dump -y <recipe>"""
        arg = [self.subcmd, '-y', 'test']
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        #print(cm.exception)
        error = cm.exception.code
        self.assertEqual(error, 0)
    
    def itest_dump_xml(self):
        """recipe_tool dump -x <recipe>"""
        arg = [self.subcmd, '-x', 'test']
        with self.assertRaises(SystemExit) as cm:
            parsed_args = self.parser.parse_args(arg)
            self.cmd(parsed_args)
        error = cm.exception.code
        self.assertEqual(error, 0)

class ExportCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'export'
        self.cmd = cmd_export


class OcrCmdTestCase(CommandLineTestCase):
    def setUp(self):
        self.subcmd = 'ocr'
        self.cmd = cmd_ocr


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
