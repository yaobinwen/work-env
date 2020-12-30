#!/usr/bin/python3
# -*- coding: utf-8 -*-


import argparse
import collections
import json
import pathlib
import sys


_field_names = [
    "Name",
    "GUID",
    "DHCP",
    "IPAddress",
    "NetworkMask",
    "IPV6Address",
    "IPV6NetworkMaskPrefixLength",
    "HardwareAddress",
    "MediumType",
    "Wireless",
    "Status",
    "VBoxNetworkName",
]


HostOnlyIF = collections.namedtuple(
    typename="HostOnlyIF",
    field_names=_field_names,
)


def _syntax():
    parser = argparse.ArgumentParser(
        description='Parse the `VBoxManage list hostonlyifs` output.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--hostonlyifs-file", "-f",
        help="The file that has the output of `VBoxManage list hostonlyifs`.",
        required=True,
    )

    parser.add_argument(
        "--if-name", "-n",
        help=(
            "Retrieve the information of the host-only network interface "
            "of this name."
        ),
        required=True,
    )

    parser.add_argument(
        "--fields",
        choices=_field_names,
        help="Retrieve the information of these fields.",
        nargs="+",
        required=True,
    )

    return parser


def main(hostonlyifs_file, if_name, fields):
    content = pathlib.Path(hostonlyifs_file).read_text(encoding="utf-8")

    hoifs = {}
    kv = {}
    for line in content.splitlines():
        # A line consists of a key and a value, separated by ":". An empty line
        # means the current block is finished and a new block will be started.

        # Note: we must not use `line.split(":")` because there can be IPv6
        # addresses in which ":" is a valid character.
        cpos = line.find(":")
        if cpos != -1:
            # This is a line inside a block. Process it.
            k = line[:cpos].strip()
            v = line[cpos+1:].strip()
            kv[k] = v
        else:
            # This is an empty line so a block is finished. Process the whole
            # block.
            assert len(line) == 0
            hoif = HostOnlyIF(**kv)
            hoifs[hoif.Name] = hoif

    hoif = hoifs[if_name]
    ret = {}
    for n in fields:
        ret[n] = getattr(hoif, n)

    print(json.dumps(ret))

    return 0


def entry_point():
    sys.exit(main(**vars(_syntax().parse_args())))


if __name__ == "__main__":
    entry_point()
