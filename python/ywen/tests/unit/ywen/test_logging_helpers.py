import argparse
import logging
import unittest

import ywen.logging_helpers as l
from ywen.test_helpers.argparse import ArgParserInspector


class TestImport(unittest.TestCase):
    def test_import(self):
        import ywen.logging_helpers


class Test_functions(unittest.TestCase):
    def test_logging_datefmt(self):
        self.assertEqual(l.logging_datefmt(), "%FT%H:%M:%S")

    def test_logging_format(self):
        self.assertEqual(
            l.logging_format(),
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
        self.assertEqual(
            l.logging_format(multiprocess=True),
            "%(asctime)s [%(levelname)s] %(name)s[%(process)d]: %(message)s",
        )

    def test_logging_level(self):
        self.assertEqual(l.log_level("debug"), logging.DEBUG)
        self.assertEqual(l.log_level("info"), logging.INFO)
        self.assertEqual(l.log_level("warning"), logging.WARNING)
        self.assertEqual(l.log_level("error"), logging.ERROR)
        self.assertEqual(l.log_level("critical"), logging.CRITICAL)


class Test_arg_logging(unittest.TestCase):
    def test_add_arg_logging(self):
        p = argparse.ArgumentParser()
        l.add_arg_logging(p)

        inspector = ArgParserInspector(arg_parser=p)

        # Do not test the internal implementation details of `argparse`.
        # self.assertTrue(inspector.has_group("positional arguments"))
        # self.assertTrue(inspector.has_group("optional arguments"))

        g = inspector.get_group("logging options")
        self.assertIsNotNone(g)

        self.assertTrue(inspector.group_has_argument(g, "--logging"))
        self.assertTrue(inspector.argument_is_deprecated("--logging"))

    def test_add_arg_logging_level(self):
        p = argparse.ArgumentParser()
        l.add_arg_logging_level(p)

        inspector = ArgParserInspector(arg_parser=p)

        # Do not test the internal implementation details of `argparse`.
        # self.assertTrue(inspector.has_group("positional arguments"))
        # self.assertTrue(inspector.has_group("optional arguments"))

        g = inspector.get_group("logging options")
        self.assertIsNotNone(g)

        self.assertTrue(inspector.group_has_argument(g, "--logging-level"))
        self.assertFalse(inspector.argument_is_deprecated("--logging-level"))


class Test_config_logging(unittest.TestCase):
    def test_config_logging(self):
        l.config_logging(
            format=l.logging_format(),
            datefmt=l.logging_datefmt(),
            log_level_str=l.LOGGING_LEVELS[0],
        )
