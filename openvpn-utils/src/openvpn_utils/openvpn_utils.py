import argparse
import csv
import logging
import pathlib
import sys
import typing

from openvpn_utils import (
    __version__,
    profile,
)
from ywen import (
    args_helpers,
    encoding,
    logging_helpers,
    units,
    version_helpers,
)


logger = logging.getLogger(pathlib.PurePath(__file__).stem)


def _syntax():
    p = argparse.ArgumentParser(description="Run OpenVPN utilities")

    version_helpers.add_arg_version(p, __version__)
    logging_helpers.add_arg_logging_level(p)

    subcmds = p.add_subparsers(
        description="available subcommands",
        dest="subcmd",
    )

    # "profile" sub-command
    profile.syntax_subcmd_profile(subcmds=subcmds)

    return p


def entry_point():
    argv_cooked = vars(_syntax().parse_args())

    logging_level = argv_cooked.pop("logging_level")
    logging_helpers.config_logging(
        format=logging_helpers.logging_format(),
        datefmt=logging_helpers.logging_datefmt(),
        log_level_str=logging_level,
    )

    func = argv_cooked.pop("func")

    sys.exit(func(logger=logger, **argv_cooked))



if __name__ == "__main__":
    entry_point()
