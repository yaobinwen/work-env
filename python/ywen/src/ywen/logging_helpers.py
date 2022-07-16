import logging

from ywen import args_helpers


LOGGING_LEVELS = [
    "debug", "info", "warning", "error", "critical",
]


def add_arg_logging(arg_parser):
    group_logging = arg_parser.add_argument_group(
        title="logging options",
    )

    d = LOGGING_LEVELS[0]
    group_logging.add_argument(
        "--logging",
        help=args_helpers.arg_help(
            help="Logging level",
            default_value=d,
            deprecated=True,
        ),
        choices=LOGGING_LEVELS,
        default=d,
    )


def add_arg_logging_level(arg_parser):
    group_logging = arg_parser.add_argument_group(
        title="logging options",
    )

    d = LOGGING_LEVELS[0]
    group_logging.add_argument(
        "--logging-level",
        help=args_helpers.arg_help(
            help="Logging level",
            default_value=d,
        ),
        choices=LOGGING_LEVELS,
        default=d,
    )


def logging_datefmt() -> str:
    return "%FT%H:%M:%S"


def logging_format(multiprocess: bool=False) -> str:
    fmt = "%(asctime)s [%(levelname)s] %(name)s[%(process)d]: %(message)s"
    if multiprocess:
        return fmt
    else:
        return fmt.replace("[%(process)d]", "")


def log_level(s: str) -> int:
    return int(getattr(logging, s.upper()))
