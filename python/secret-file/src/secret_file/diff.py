# standard
import pathlib

# 3rd-party
from ywen import (
    subprocess,
    tempfile,
)

# ours
from secret_file import decrypt


_PREFIX = "secret-file.diff"


def _do_subcmd_diff(
    logger,
    subcmd: str,
    encrypted_file: pathlib.Path,
):

    # Get the decrypted file in the working directory.
    parent = encrypted_file.parent
    fname = encrypted_file.name
    decrypted_file = parent / fname[: -len(".vaulted")]

    # If the decrypted file doesn't exist, that means we didn't change anything
    # in the encrypted file so it is the latest.
    if not decrypted_file.exists():
        print(
            f"'{encrypted_file}' is the latest "
            "(because the local decrypted file doesn't exist)."
        )
        return 0

    if not decrypted_file.is_file():
        raise RuntimeError(f"'{encrypted_file}' is not a regular file")

    with tempfile.temp_dir(prefix=_PREFIX) as tmp_dir:
        decrypted_file_2 = decrypt._do_subcmd_decrypt(
            logger=logger,
            subcmd="de",
            encrypted_file=encrypted_file,
            output_dir=tmp_dir,
        )

        cmd = [
            "diff",
            decrypted_file,
            decrypted_file_2,
        ]
        rc, stdout_str, stderr_str = subprocess.run(
            cmd=cmd,
            check=False,
        )

        if rc == 0:
            print(f"'{encrypted_file}' is the latest.")
            return 0
        elif rc == 1:
            print(f"'{encrypted_file}' is NOT the latest.")
            print("diff:")
            print(f"< {decrypted_file}")
            print(f"> {encrypted_file}")
            print("=" * 10)
            print(stdout_str)
            return 0
        else:
            raise subprocess.CalledProcessError(
                returncode=rc,
                cmd=cmd,
                stderr=stderr_str,
            )


def syntax_subcmd_diff(subcmds):
    desc = "Check if the encrypted file is the latest"
    subcmd = subcmds.add_parser("diff", description=desc, help=desc)
    subcmd.set_defaults(func=_do_subcmd_diff)

    subcmd.add_argument(
        "encrypted_file",
        metavar="PATH",
        help="Path of the encrypted file to be checked",
        type=pathlib.Path,
    )
