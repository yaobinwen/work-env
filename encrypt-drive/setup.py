import io
import pathlib
from setuptools import setup, find_packages

from ywen import debian
from ywen.encoding import PREFERRED_ENCODING


DEBIAN_CHANGELOG = pathlib.Path(__file__).parent / "debian" / "changelog"
REQUIREMENTS_TXT = pathlib.Path(__file__).parent / "requirements.txt"


def _requirements(
    *,
    requirements_file: pathlib.Path,
):
    with io.open(requirements_file, "r", encoding=PREFERRED_ENCODING) as fh:
        return [line.rstrip("\n") for line in fh]


def entry_point():
    changelog = debian.Changelog(changelog=DEBIAN_CHANGELOG)

    setup(
        name=changelog.Source,
        version=changelog.Version.upstream,
        maintainer=changelog.Maintainer.name,
        maintainer_email=changelog.Maintainer.email,
        url="https://github.com/yaobinwen/work-env",
        package_dir={"": "src"},
        packages=find_packages(where="src"),
        install_requires=_requirements(requirements_file=REQUIREMENTS_TXT),
        include_package_data=True,
        entry_points={
            "console_scripts": [
                "ywen-encrypt-drive = encrypt_drive.encrypt_drive:entry_point",
            ]
        },
    )


if __name__ == "__main__":
    entry_point()
