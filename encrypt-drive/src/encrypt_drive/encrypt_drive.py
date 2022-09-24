# standard
import argparse
import getpass
import json
import logging
import os
import pathlib
import re
import sys
import typing

# ours
from ywen import (
    encoding,
    logging_helpers,
    subprocess,
)


logger = logging.getLogger(pathlib.PurePath(__file__).stem)


_VOLUME_LABEL_REGEX = re.compile(pattern=r"^[\w-]{1,16}$")


def _syntax():
    # TODO(ywen): Provide a concise description.
    p = argparse.ArgumentParser(description="")

    p.add_argument(
        "--partition",
        help="The partition to be encrypted (e.g., /dev/sdb1).",
        type=pathlib.Path,
    )

    p.add_argument(
        "--volume-label",
        help="The label of the encrypted volume.",
    )

    # TODO(ywen): Do not display it or use other means to transfer the
    # passphrase.
    p.add_argument(
        "--passphrase",
        help="The passphrase for decryption",
    )

    logging_helpers.add_arg_logging_level(p)

    return p


class NotBlockDeviceError(Exception):
    """Raised when the partition is not a block device."""

    pass


class PartitionNotFoundError(Exception):
    """Raised when the partition is not found."""

    pass


def _privileged_main(
    partition: pathlib.Path,
    volume_label: str,
    passphrase: str,
):
    virtual_device_name = "ywen_encrypt_drive"

    ans = [
        "YES",  # `luksFormat` asks the user for confirmation before formatting
        passphrase,  # enter passphrase
        passphrase,  # verify passphrase
    ]
    _, stdout_str, stderr_str = subprocess.run(
        cmd=[
            "cryptsetup",
            "luksFormat",
            str(partition),
        ],
        input=("\n".join(ans) + "\n"),
        check=True,
    )
    print(stdout_str)
    print(stderr_str)

    _, stdout_str, stderr_str = subprocess.run(
        cmd=[
            "cryptsetup",
            "luksOpen",
            str(partition),
            virtual_device_name,
        ],
        input=(passphrase + "\n"),
        check=True,
    )
    print(stdout_str)
    print(stderr_str)

    _, stdout_str, stderr_str = subprocess.run(
        cmd=[
            "mkfs.ext4",
            f"/dev/mapper/{virtual_device_name}",
            "-L",
            volume_label,
        ],
        check=True,
    )
    print(stdout_str)
    print(stderr_str)

    _, stdout_str, stderr_str = subprocess.run(
        cmd=[
            "cryptsetup",
            "luksClose",
            virtual_device_name,
        ],
        check=True,
    )
    print(stdout_str)
    print(stderr_str)


def _lsblk():
    _, stdout_str, _ = subprocess.run(
        cmd=[
            "lsblk",
            "--json",
        ],
    )
    return json.loads(stdout_str)["blockdevices"]


def _find_block_device(device: str, blockdevices: typing.List[typing.Dict[str, str]]):
    for d in blockdevices:
        if f"/dev/{d['name']}" == device:
            return d

        if "children" in d:
            for c in d["children"]:
                if f"/dev/{c['name']}" == device:
                    return c

    return None


def _unprivileged_main(
    partition: pathlib.Path,
    volume_label: str,
    passphrase: str,
):
    if passphrase is not None:
        raise ValueError("passphrase should not be set on command line")

    # Make sure `partition` is a block device.
    if not partition.is_block_device():
        raise NotBlockDeviceError(f"'{partition}' is not a block device")

    # Make sure `partition` exists.
    blockdevices = _lsblk()
    blockdevice = _find_block_device(
        device=str(partition),
        blockdevices=blockdevices,
    )
    if blockdevice is None:
        raise PartitionNotFoundError(
            f"'{partition}' is not a partition (available: {blockdevices})",
        )

    if _VOLUME_LABEL_REGEX.match(volume_label) is None:
        raise ValueError(f"'{volume_label}' is not a valid volume label")

    # Get sudo password.
    user = getpass.getuser()
    sudo_pass = getpass.getpass(prompt=f"[sudo] password for {user}: ")

    # Get encrypted disk passphrase.
    passphrase_match = False
    while not passphrase_match:
        passphrase = getpass.getpass(
            prompt="Enter passphrase for decryption: ",
        )
        passphrase2 = getpass.getpass(
            prompt="Verify passphrase: ",
        )
        passphrase_match = passphrase == passphrase2
        if not passphrase_match:
            print("Passphrases do not match. Try again.")

    # Launch the priviledged version.
    try:
        rc, stdout_str, stderr_str = subprocess.run(
            cmd=[
                "sudo",
                "--stdin",
                # TODO(ywen): Do not use absolute path.
                "/home/ywen/.local/bin/ywen-encrypt-drive",
                "--partition",
                str(partition),
                "--volume-label",
                volume_label,
                "--passphrase",
                passphrase,
            ],
            input=sudo_pass + "\n",  # This '\n' got me!
            encoding=encoding.PREFERRED_ENCODING,
            check=True,
        )
        print(stdout_str)
    except subprocess.CalledProcessError as ex:
        logger.exception(ex)
        logger.error("stdout: %s", ex.stdout)
        logger.error("stderr: %s", ex.stderr)


def _main(
    partition: pathlib.Path,
    volume_label: str,
    passphrase: str,
    logging_level: str,
):
    logging_helpers.config_logging(
        format=logging_helpers.logging_format(),
        datefmt=logging_helpers.logging_datefmt(),
        log_level_str=logging_level,
    )

    euid = os.geteuid()
    if euid == 0:
        _privileged_main(partition, volume_label, passphrase)
    else:
        _unprivileged_main(partition, volume_label, passphrase)


def entry_point():
    sys.exit(_main(**vars(_syntax().parse_args())))


if __name__ == "__main__":
    entry_point()
