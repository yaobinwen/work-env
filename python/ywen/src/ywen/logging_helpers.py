import logging

from ywen import args_helpers


def add_arg_logging_level(arg_parser):
    group_logging = arg_parser.add_argument_group(
        title="logging options",
    )

    d = "debug"
    group_logging.add_argument(
        "--logging",
        help=args_helpers.arg_help_with_default(
            help="Logging level",
            default=d,
        ),
        choices=[
            "debug", "info", "warning", "error", "critical",
        ],
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
