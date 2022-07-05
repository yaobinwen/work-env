import argparse


def add_arg_version(
    arg_parser: argparse.ArgumentParser,
    version: str,
):
    arg_parser.add_argument(
        "--version",
        action="version",
        version=version,
    )
