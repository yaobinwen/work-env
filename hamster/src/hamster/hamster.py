#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import logging
import sys
from pathlib import Path, PurePath

from hamster.git_repo import Repo
from hamster.run import run


loggerName = PurePath(PurePath(__file__).name).stem
logger = logging.getLogger(loggerName)


def _build(repo, remote_branch, pkg_paths):
    repo.checkout(
        local_branch="hamster-build",
        remote_branch=remote_branch,
    )

    for p in pkg_paths:
        dpath = repo.working_copy_dir.joinpath(p)
        run(
            cmd=["python3", "setup.py", "sdist", "bdist_wheel"],
            cwd=str(dpath),
        )


def _get_last_HEAD(hamster_dir, remote_branch):
    remote_branch_dir = Path(hamster_dir).joinpath(".hamster", remote_branch)
    if not remote_branch_dir.is_dir():
        # This remote branch has never been dealt with before so we don't have
        # the HEAD information of the last time.
        return None

    last_HEAD_fpath = remote_branch_dir.joinpath("last_HEAD")
    if not last_HEAD_fpath.is_file():
        # We haven't recorded the HEAD commit yet.
        return None

    last_HEAD = last_HEAD_fpath.read_text(encoding="utf-8").strip()


def _has_new_code(hamster_dir, repo, remote_branch):
    head_before = _get_last_HEAD(hamster_dir, remote_branch)
    repo.fetch()
    head_after = repo.current_HEAD(remote_branch)

    return head_after != head_before


def _publish(repo, pkg_paths):
    repo.switch("hamster-build")

    for p in pkg_paths:
        dpath = repo.working_copy_dir.joinpath(p)
        run(
            cmd=[
                "twine",
                "upload",
                "--repository-url",
                "http://localhost:18081/repository/pypi-internal/",
                "--username",
                "ywen",
                "--password",
                "s3cr3t",   # TODO(ywen): Use ansible-vault
                "dist/*"],
            cwd=str(dpath),
        )

    repo.switch("master")


def _sanity_check():
    pass


def _test_publilshing(repo, pkg_paths):
    repo.switch("hamster-build")

    for p in pkg_paths:
        dpath = repo.working_copy_dir.joinpath(p)
        run(
            cmd=[
                "twine",
                "upload",
                "--repository-url",
                "http://localhost:18081/repository/pypi-snapshot/",
                "--username",
                "ywen",
                "--password",
                "s3cr3t",   # TODO(ywen): Use ansible-vault
                "dist/*"],
            cwd=str(dpath),
        )

    repo.switch("master")


def _syntax():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--remote-branch",
        help="The remote branch to find the Python packages.",
        default="origin/master",
    )

    # TODO(ywen): This should be deduced from the repository URI.
    parser.add_argument(
        "--working-copy-name",
        help="The name of the working copy directory.",
        required=True,
    )

    parser.add_argument(
        "--repo-uri",
        help="The URI of the Git repository.",
        required=True,
    )

    # TODO(ywen): Reorder the arguments.
    parser.add_argument(
        "--hamster-dir", "-d",
        help="The directory in which all the repositories are cloned.",
    )

    return parser


# TODO(ywen): Reorder arguments.
def main(remote_branch, repo_uri, hamster_dir, working_copy_name):
    logging.basicConfig(
        # filename="hamster.log",
        # filemode="w",
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
        level=logging.DEBUG,
    )

    repo = Repo(repo_uri, working_copy_name, hamster_dir)

    if not _has_new_code(hamster_dir, repo, remote_branch):
        logger.info(f"No new code.")
        return 0

    try:

        _build(repo, remote_branch, ["."])

        _test_publilshing(repo, ["."])

        _publish(repo, ["."])

        return 0

    except Exception as ex:
        logger.exception(str(ex))
        raise
    finally:
        repo.remove_branch("hamster-build", "master")
        repo.clean()


def entry_point():
    sys.exit(main(**vars(_syntax().parse_args())))


if __name__ == "__main__":
    entry_point()
