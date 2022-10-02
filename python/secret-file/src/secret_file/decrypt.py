# standard
import pathlib

# 3rd-party
from ywen import (
    subprocess,
)


def _do_subcmd_decrypt(
    logger,
    subcmd: str,
    encrypted_file: pathlib.Path,
    output_dir: pathlib.Path,
):
    parent = encrypted_file.parent if output_dir is None else output_dir
    fname = encrypted_file.name
    if not fname.endswith(".vaulted"):
        raise ValueError(f"'{encrypted_file}' doesn't not end with '.vaulted'")

    decrypted_file = parent / fname[: -len(".vaulted")]

    subprocess.run(
        cmd=[
            "ansible-vault",
            "decrypt",
            "--output",
            str(decrypted_file),
            str(encrypted_file),
        ],
        check=True,
    )

    return decrypted_file


def syntax_subcmd_decrypt(subcmds):
    desc = "Decrypt the given file"
    subcmd = subcmds.add_parser("de", description=desc, help=desc)
    subcmd.set_defaults(func=_do_subcmd_decrypt)

    subcmd.add_argument(
        "encrypted_file",
        metavar="PATH",
        help="Path of the encrypted file to be decrypted",
        type=pathlib.Path,
    )

    subcmd.add_argument(
        "--output-dir",
        metavar="PATH",
        help="Path of directory to put the decrypted file",
        type=pathlib.Path,
    )
