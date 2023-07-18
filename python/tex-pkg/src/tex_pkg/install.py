# standard
import logging
import pathlib
import urllib.parse as url_parser

# 3rd-party
from ywen import (
    subprocess,
    tempfile,
)


logger = logging.getLogger(pathlib.PurePath(__file__).stem)


def _check_tools():
    for tool in ["curl", "unzip", "latex", "mktexlsr"]:
        subprocess.run(
            cmd=["which", tool],
            check=True,
        )


def _do_subcmd_install(
    logger,
    subcmd: str,
    zip_uri,
    texmf_dir,
    pkg_root_subdir,
    no_delete_tmp_dirs,
):
    # Make sure the needed tools are all installed.
    _check_tools()

    pkg_root_path = texmf_dir / pkg_root_subdir

    parsed_uri = url_parser.urlparse(zip_uri)
    pkg_uri_path = pathlib.Path(parsed_uri.path)
    pkg_fname = pkg_uri_path.name
    pkg_name = pkg_uri_path.stem

    logger.info("CTAN package link: %s", zip_uri)
    logger.info("package filename: %s", pkg_fname)
    logger.info("package name: %s", pkg_name)
    logger.info("texmf path: %s", texmf_dir)
    logger.info("Tex package root dir: %s", pkg_root_path)

    # Check if the package is already installed.
    pkg_install_path = pkg_root_path / pkg_name
    if pkg_install_path.is_dir():
        logger.warning(
            "package seems to already exist: '%s' (installation skipped)",
            pkg_install_path,
        )
        return

    logger.info("making %s...", pkg_root_path)
    subprocess.run(
        cmd=[
            "mkdir",
            "-p",
            pkg_root_path,
        ],
        check=True,
    )

    with tempfile.temp_dir(
        prefix="tex-pkg.",
        delete=(not no_delete_tmp_dirs),
    ) as tmp_dir:
        cmd = [
            "curl",
            "-o",
            pkg_fname,
            "-L",  # Follow the redirection link
            zip_uri,
        ]
        logger.info("downloading package zip file: '%s'", " ".join(cmd))
        subprocess.run(
            cmd=cmd,
            cwd=tmp_dir,
            check=True,
        )

        logger.info("unzipping package zip file...")
        subprocess.run(
            cmd=[
                "unzip",
                pkg_fname,
            ],
            cwd=tmp_dir,
            check=True,
        )

        unzipped_pkg_dir = tmp_dir / pkg_name
        sty_fpath = unzipped_pkg_dir / (pkg_name + ".sty")
        ins_fname = unzipped_pkg_dir / (pkg_name + ".ins")
        dtx_fname = unzipped_pkg_dir / (pkg_name + ".dtx")
        if not sty_fpath.is_file():
            for fname in [ins_fname, dtx_fname]:
                cmd = [
                    "latex",
                    fname,
                    pkg_root_path,
                ]
                logger.info("running '%s'...", str(cmd))
                subprocess.run(
                    cmd=cmd,
                    cwd=unzipped_pkg_dir,
                    check=True,
                )

        # No need to generate the .sty file so we can move the files
        # directly.
        logger.info("moving package into '%s'", pkg_root_path)
        subprocess.run(
            cmd=[
                "mv",
                unzipped_pkg_dir,
                pkg_root_path,
            ],
            check=True,
        )

    # Update ls-R
    logger.info("updating ls-R (may need sudo)...")
    subprocess.run(
        cmd=[
            "sudo",
            "mktexlsr",
        ],
        check=True,
    )


def syntax_subcmd_install(subcmds):
    desc = "Install the Tex package from CTAN"
    subcmd = subcmds.add_parser("install", description=desc, help=desc)
    subcmd.set_defaults(func=_do_subcmd_install)

    subcmd.add_argument(
        "zip_uri",
        metavar="URI",
        help="URI of the Tex package's zip file",
        type=str,
    )

    subcmd.add_argument(
        "--texmf-dir",
        default=pathlib.Path("/usr/local/share/texmf"),
        metavar="PATH",
        help="Path of the texmf directory",
        type=pathlib.Path,
    )

    subcmd.add_argument(
        "--pkg-root-subdir",
        default=pathlib.Path("tex/latex"),
        metavar="PATH",
        help=(
            "Sub-directory under texmf directory where all the CTAN package "
            "will be installed"
        ),
        type=pathlib.Path,
    )

    g = subcmd.add_argument_group("debugging options")
    g.add_argument(
        "--no-delete-tmp-dirs",
        default=False,
        action="store_true",
        help="Do not delete the temporary directories",
    )
