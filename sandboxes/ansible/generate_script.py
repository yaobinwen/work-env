#!/usr/bin/python3

import argparse
import io
import os.path
import stat


def _syntax():
    parser = argparse.ArgumentParser(description="Parse the CLI options.")
    parser.add_argument(
        "--destroy",
        help="Destroy the virtual machine when the playbook is finished.",
        action="store_true",
    )
    parser.add_argument(
        "--halt",
        help="Halt the virtual machine when the playbook is finished.",
        action="store_true",
    )
    parser.add_argument(
        "--script-dir",
        help="The path of the directory where the script is generated.",
        required=True,
    )
    parser.add_argument(
        "--script-file-name", help="The script file name.", required=True,
    )
    return parser


def _main(destroy, halt, script_dir, script_file_name):
    lines = [
        "#!/bin/sh",
        "set -ex",
        "vagrant up",
        "vagrant provision --provision-with 'sandbox-play'",
    ]

    if destroy:
        lines.append("vagrant destroy --force")
    elif halt:
        lines.append("vagrant halt")

    fpath = os.path.join(script_dir, script_file_name)
    with io.open(fpath, "w", encoding="utf-8") as fh:
        for line in lines:
            fh.write(line + "\n")

    os.chmod(path=fpath, mode=stat.S_IRWXU)


if __name__ == "__main__":
    _main(**vars(_syntax().parse_args()))
