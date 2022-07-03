import io
import pathlib
import re
import subprocess
import typing

from collections import namedtuple
from setuptools import setup, find_namespace_packages


DEBIAN_CHANGELOG = pathlib.Path(__file__).parent / "debian" / "changelog"
REQUIREMENTS_TXT = pathlib.Path(__file__).parent / "requirements.txt"

REGEX_MAINTAINER = re.compile(
    r"^([\w\d\s]+)\s\<([\w\d\s\-\._]+\@[\w\d\-_]+\.[\w\d]+)\>$"
)


def _run(
    *,
    cmd: typing.List[str],
    cwd: pathlib.Path=None,
    check: bool=True,
) -> typing.Tuple[int, str, str]:
    cp = subprocess.run(
        args=cmd,
        cwd=cwd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        check=check,
    )

    stdout_str = cp.stdout.decode("utf-8")
    stderr_str = cp.stderr.decode("utf-8")

    if cp.returncode != 0:
        raise subprocess.CalledProcessError(
            f"Command '{cmd}' returned non-zero exit status {cp.returncode}: "
            f"{stderr_str}"
        )

    return cp.returncode, stdout_str, stderr_str


def _upstream_field(
    *,
    changelog: pathlib.Path,
    field: str,
):
    _, stdout_str, _ = _run(
        cmd=[
            "dpkg-parsechangelog",
            "--file",
            changelog,
            "--show-field",
            field,
        ],
    )

    return stdout_str.rstrip("\n")


def _upstream_name(
    *,
    changelog: pathlib.Path,
):
    return _upstream_field(changelog=changelog, field="Source")


def _upstream_version(
    *,
    changelog: pathlib.Path,
):
    value = _upstream_field(changelog=changelog, field="Version")
    return value[0:value.find("-")]


def _upstream_maintainer(
    *,
    changelog: pathlib.Path,
):
    value = _upstream_field(changelog=changelog, field="Maintainer")

    m = REGEX_MAINTAINER.match(value)
    if m is None:
        raise ValueError(f"'{value}' does not match the maintainer format.")

    return (m.group(1), m.group(2))


def _requirements(
    *,
    requirements_file: pathlib.Path,
):
    with io.open(requirements_file, "r", encoding="UTF-8") as fh:
        return [line.rstrip("\n") for line in fh]


def main():
    name = _upstream_name(changelog=DEBIAN_CHANGELOG)
    version = _upstream_version(changelog=DEBIAN_CHANGELOG)
    maintainer_name, maintainer_email = _upstream_maintainer(
        changelog=DEBIAN_CHANGELOG
    )
    requirements = _requirements(requirements_file=REQUIREMENTS_TXT)

    setup(
        name=name,
        version=version,
        maintainer=maintainer_name,
        maintainer_email=maintainer_email,
        url="https://github.com/yaobinwen/work-env",
        package_dir={"": "src"},
        packages=find_namespace_packages(where="src"),
        install_requires=requirements,
        include_package_data=True,
        entry_points={},
    )


if __name__ == "__main__":
    main()
