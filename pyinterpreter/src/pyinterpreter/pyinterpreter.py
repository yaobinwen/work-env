import argparse
import logging
import pathlib
import sys

from pyinterpreter import __version__
from ywen import (
    args_helpers,
    logging_helpers,
    subprocess,
    version_helpers,
)


logger = logging.getLogger(pathlib.PurePath(__file__).stem)


def _syntax():
    p = argparse.ArgumentParser(
        description=("Run Python script using latest/specific Python interpreter"),
    )

    version_helpers.add_arg_version(p, __version__)
    logging_helpers.add_arg_logging_level(p)

    d = "latest"
    p.add_argument(
        "--py-version",
        metavar="VERSION",
        help=args_helpers.arg_help_with_default(
            help="Version of the Python interpreter to use",
            default=d,
        ),
        default=d,
    )

    d = "my-running-python-script"
    p.add_argument(
        "--container-name",
        metavar="NAME",
        help=args_helpers.arg_help_with_default(
            help="Container name",
            default=d,
        ),
        default=d,
    )

    p.add_argument(
        "py_file_path",
        metavar="PATH",
        help="Path of the Python script to run",
        type=pathlib.Path,
    )

    return p


def _main(
    *,
    logger,
    py_version: str,
    container_name: str,
    py_file_path: pathlib.Path,
):
    logger.info("Desired Python version: %s", py_version)
    logger.info("Python script path: %s", py_file_path)

    py_dir = py_file_path.parent
    py_fname = py_file_path.name
    logger.info("Python script folder: %s", py_dir)
    logger.info("Python script filename: %s", py_fname)

    cmd = [
        "docker",
        "run",
        "-it",
        "--rm",
        "--name",
        container_name,
        "-v",
        f"{str(py_dir)}:/usr/src/myapp",
        "-w",
        "/usr/src/myapp",
        f"python:{py_version}",
        "python",
        str(py_fname),
    ]

    logger.info("Docker command: %s", " ".join(cmd))

    with subprocess.run_query_stdout(
        cmd=[
            "docker",
            "run",
            "-it",
            "--rm",
            "--name",
            container_name,
            "-v",
            f"{str(py_dir)}:/usr/src/myapp",
            "-w",
            "/usr/src/myapp",
            f"python:{py_version}",
            "python",
            str(py_fname),
        ],
        check=True,
    ) as q:
        for line in q:
            print(line)


def entry_point():
    argv_cooked = vars(_syntax().parse_args())

    logging_level = argv_cooked.pop("logging_level")
    logging_helpers.config_logging(
        format=logging_helpers.logging_format(),
        datefmt=logging_helpers.logging_datefmt(),
        log_level_str=logging_level,
    )

    sys.exit(_main(logger=logger, **argv_cooked))


if __name__ == "__main__":
    entry_point()
