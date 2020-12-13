# -*- coding: utf-8 -*-

import logging
from pathlib import Path, PurePath

from hamster.run import run


loggerName = PurePath(PurePath(__file__).name).stem
logger = logging.getLogger(loggerName)


class Repo(object):
    def __init__(self, repo_uri, working_copy_name, hamster_dir):
        self.hamster_dir = Path(hamster_dir)
        self.repo_uri = repo_uri
        self.working_copy_name = working_copy_name
        self.working_copy_dir = self.hamster_dir.joinpath(working_copy_name)
        self.landing_branch = "master"

        if not self.working_copy_dir.is_dir():
            logger.info(
                f"'{self.working_copy_dir}' doesn't exist. Clone the repo."
            )
            self._run(
                cmd=["git", "clone", self.repo_uri, self.working_copy_name],
                cwd=str(self.hamster_dir),
            )
        else:
            logger.info(
                f"'{self.working_copy_dir}' already exists. Skip cloning."
            )

    def _run(self, cmd, cwd):
        return run(cmd=cmd, cwd=cwd, timeout=900)

    def checkout(self, local_branch, remote_branch):
        self._run(
            cmd=["git", "branch", local_branch, remote_branch],
            cwd=str(self.working_copy_dir),
        )
        self._run(
            cmd=["git", "checkout", local_branch],
            cwd=str(self.working_copy_dir),
        )

    def clean(self):
        self._run(
            cmd=["git", "clean", "-x", "-f", "."],
            cwd=str(self.working_copy_dir),
        )

    def current_HEAD(self, remote_branch):
        ret = self._run(
            cmd=["git", "rev-parse", remote_branch],
            cwd=str(self.working_copy_dir),
        )

        # `ret.stdout` is the commit SHA-1 checksum but may contain "\n", hence
        # strip().
        return ret.stdout.strip()

    def fetch(self):
        self._run(
            cmd=["git", "fetch"],
            cwd=str(self.working_copy_dir),
        )

    def remove_branch(self, branch_to_remove, landing_branch):
        self.switch(landing_branch)
        self._run(
            cmd=["git", "branch", "-D", branch_to_remove],
            cwd=str(self.working_copy_dir),
        )

    def switch(self, local_branch):
        self._run(
            cmd=["git", "checkout", local_branch],
            cwd=str(self.working_copy_dir),
        )
