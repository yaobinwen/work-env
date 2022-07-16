import unittest

import ywen.args_helpers as h


class TestImport(unittest.TestCase):
    def test_import(self):
        import ywen.args_helpers


class Test_helpers(unittest.TestCase):
    def test_arg_help(self):
        self.assertEqual(h.arg_help(help="help"), "help")
        self.assertEqual(
            h.arg_help(help="help", default_value="123"),
            "help (default: 123)",
        )
        self.assertEqual(
            h.arg_help(help="help", deprecated=True),
            f"{h.DEPRECATION_TAG} help",
        )
        self.assertEqual(
            h.arg_help(help="help", default_value="123", deprecated=True),
            f"{h.DEPRECATION_TAG} help (default: 123)",
        )

    def test_arg_help_with_default(self):
        self.assertEqual(
            h.arg_help_with_default(help="help", default="0"),
            "help (default: 0)"
        )

    def test_arg_help_with_deprecation_warning(self):
        self.assertEqual(
            h.arg_help_with_deprecation_warning(help="help"),
            f"{h.DEPRECATION_TAG} help"
        )
