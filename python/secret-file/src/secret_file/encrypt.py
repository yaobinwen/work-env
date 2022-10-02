# standard
import pathlib

# 3rd-party
from ywen import (
    subprocess,
)


def _do_subcmd_encrypt(
    logger,
    subcmd: str,
    decrypted_file: pathlib.Path,
    label: str,
    output_dir: pathlib.Path,
):
    parent = decrypted_file.parent if output_dir is None else output_dir
    fname = decrypted_file.name
    encrypted_file = parent / (fname + ".vaulted")

    subprocess.run(
        cmd=[
            "ansible-vault",
            "encrypt",
            "--vault-id",
            f"{label}@prompt",
            "--output",
            str(encrypted_file),
            str(decrypted_file),
        ],
        check=True,
    )

    return encrypted_file


def syntax_subcmd_encrypt(subcmds):
    desc = "Encrypt the given file"
    subcmd = subcmds.add_parser("en", description=desc, help=desc)
    subcmd.set_defaults(func=_do_subcmd_encrypt)

    subcmd.add_argument(
        "decrypted_file",
        metavar="PATH",
        help="Path of the decrypted file to be encrypted",
        type=pathlib.Path,
    )

    subcmd.add_argument(
        "label",
        metavar="LABEL",
        help="Ansible Vault ID label",
    )

    subcmd.add_argument(
        "--output-dir",
        metavar="PATH",
        help="Path of directory to put the encrypted file",
        type=pathlib.Path,
    )
