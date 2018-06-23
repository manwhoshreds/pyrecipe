import sys
import unittest

from pyrecipe.__main__ import get_parser

class CommandLineTestCase(unittest.TestCase):
    """
    Base TestCase class, sets up a CLI parser
    """
    @classmethod
    def setUpClass(cls):
        parser = get_parser()
        cls.parser = parser

#class RecipeTestCase(CommandLineTestCase):
class RecipeTestCase(CommandLineTestCase):
    def test_with_empty_args(self):
        """User passes no args, and should be offered help."""
        args = self.parser.parse_args([])
        result = str(self.parser.print_help())
        self.assertEqual(type(args), result)

    #def test_db_servers_ubuntu_ami_in_australia():
    #    """
    #    Find database servers with the Ubuntu AMI in Australia region
    #    """
    #    args = self.parser.parse_args(['database', '-R', 'australia', '-A', 'idbs81839'])
    #    result = ping(args.tags, args.region, args.ami)
    #    self.assertIsNotNone(result)
    #    # Do some othe assertions on the result

if __name__ == "__main__":
    unittest.main()
