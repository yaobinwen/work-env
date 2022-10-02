import argparse
import logging
import pathlib
import sys

from secret_file import (
    __version__,
    decrypt,
    diff,
    encrypt,
)
from ywen import (
    logging_helpers,
    version_helpers,
)


logger = logging.getLogger(pathlib.PurePath(__file__).stem)


def _syntax():
    p = argparse.ArgumentParser(description="Handle the secret files")

    version_helpers.add_arg_version(p, __version__)
    logging_helpers.add_arg_logging_level(p)

    subcmds = p.add_subparsers(
        description="available subcommands",
        dest="subcmd",
    )

    # "en" sub-command
    encrypt.syntax_subcmd_encrypt(subcmds=subcmds)

    # "de" sub-command
    decrypt.syntax_subcmd_decrypt(subcmds=subcmds)

    # "diff" sub-command
    diff.syntax_subcmd_diff(subcmds=subcmds)

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
