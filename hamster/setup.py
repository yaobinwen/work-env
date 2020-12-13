# References:
# [1] https://github.com/pypa/sampleproject


import setuptools
import pathlib


def _read_requirements(fpath):
    content = fpath.read_text(encoding="utf-8")
    return content.splitlines()


def main():
    here = pathlib.Path(__file__).parent.resolve()

    # Get the long description from the README file.
    long_description = (here / "README.md").read_text(encoding="utf-8")

    # Get the required packages.
    install_requires = _read_requirements(here / "requirements.txt")

    setuptools.setup(
        description="Hamster: a small Python packaging and publishing utility",
        entry_points={
            "console_scripts": [
                (
                    "hamster = "
                    "hamster.hamster:entry_point"
                ),
            ]
        },
        install_requires=install_requires,
        long_description=long_description,
        long_description_content_type="text/markdown",
        maintainer="Yaobin (Robin) Wen",
        maintainer_email="robin.wyb@gmail.com",
        name="hamster",
        packages=setuptools.find_packages(where="src"),
        package_dir={"": "src"},
        python_requires=">=3.6",
        version="0.0.1",
    )


if __name__ == "__main__":
    main()
