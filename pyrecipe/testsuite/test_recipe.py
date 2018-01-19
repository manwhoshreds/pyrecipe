import unittest

from pyrecipe.ingredient import IngredientParser

class IngredientTestCase(unittest.TestCase):

    def test_ingred_parser_equal_to(self):
        ingred = IngredientParser()
        ingred_strs = [('1 large tablespoon onion, chopped',
                          [1, 'large', 'tablespoon', 'onion', 'chopped']),
                       
                       ('3 large tablespoons onion, minced',
                          [3, 'large', 'tablespoon', 'onion', 'minced']),
                       
                       ('1 onion, chopped',
                          [1, '', 'each', 'onion', 'chopped']),
                       
                       ('.1 onion, chopped',
                          [.1, '', 'each', 'onion', 'chopped'])]


        for item, expected in ingred_strs:
            self.assertEqual(ingred.parse(item), expected)

if __name__ == '__main__':
    unittest.main()
