import argparse
import typing

from ywen.args_helpers import DEPRECATION_TAG


class ArgumentNotFound(Exception):
    """Raised when an argument is not found.
    """
    pass


class GroupNotFound(Exception):
    """Raised when an argument group is not found.
    """
    pass


class ArgParserInspector(object):
    def __init__(
        self,
        arg_parser: argparse.ArgumentParser,
    ):
        self.arg_parser = arg_parser

    def get_group(
        self,
        title: str,
    ) -> typing.Union["argparse._ArgumentGroup", None]:
        for g in self.arg_parser._action_groups:
            if g.title == title:
                return g

        return None

    def has_group(
        self,
        title: str,
    ) -> bool:
        return self.get_group(title) is not None

    def get_argument(
        self,
        arg_name: str,
    ) -> typing.Union["argparse.Action", None]:
        for a in self.arg_parser._actions:
            if arg_name in a.option_strings:
                return a

        return None

    def has_argument(
        self,
        arg_name: str,
    ) -> bool:
        return self.get_argument(arg_name) is not None

    def group_has_argument(
        self,
        group: typing.Union["argparse._ArgumentGroup", str],
        arg_name: str,
    ) -> bool:
        g = group

        if isinstance(group, str):
            title = group
            g = self.get_group(title)
            if g is None:
                raise GroupNotFound(
                    f"Group '{title}' is not found in the parser."
                )

        defined_arguments = set()
        for a in g._actions:
            defined_arguments.update(a.option_strings)

        return arg_name in defined_arguments

    def argument_is_deprecated(
        self,
        arg_name: str,
    ) -> bool:
        a = self.get_argument(arg_name)
        if a is None:
            raise ArgumentNotFound(
                f"Argument '{arg_name}' is not found in the parser."
            )

        return a.help.startswith(DEPRECATION_TAG)
