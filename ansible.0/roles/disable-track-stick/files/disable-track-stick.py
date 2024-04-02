#!/usr/bin/env python3


import argparse
import re
import shutil
import subprocess
import sys


class _PyVersion(object):

    def __init__(self, major, minor, micro):
        self._major = major
        self._minor = minor
        self._micro = micro

    def __str__(self):
        return '{m1}.{m2}.{m3}'.format(
            m1=self._major,
            m2=self._minor,
            m3=self._micro,
        )

    def greater_than(self, ver):
        if self._major > ver[0]:
            return True
        if self._minor > ver[1]:
            return True
        if self._micro > ver[2]:
            return True
        return False


_MIN_PY_VER = _PyVersion(3, 6, 8)


def _pre_flight_check():
    # Check if we are using the desired Python version.
    py_ver = sys.version_info
    if _MIN_PY_VER.greater_than(sys.version_info):
        raise RuntimeError('Minimal Python version {mv} is required but currently is {cv}'.format(
            mv=str(_MIN_PY_VER), cv=sys.version_info
        ))

    # Check if we have `xinput` installed.
    if shutil.which('xinput') is None:
        raise RuntimeError('Required tool "xinput" is not installed.')


def _take_off():
    ret = subprocess.run(
        ['xinput', 'list'],
        stdout=subprocess.PIPE,
    )
    str_lines = ret.stdout.decode('utf-8')
    lines = str_lines.split('\n')

    regex = re.compile(r'^.+DualPoint\sStick\s+id=([0-9]+)\s\[slave\s+pointer.*\]')

    did = None  # device ID
    for line in lines:
        m = regex.match(line)
        if m is not None:
            did = m.group(1)
            break
    
    ret = subprocess.run(
        ['xinput', '-list-props', did],
        stdout=subprocess.PIPE,
    )
    str_lines = ret.stdout.decode('utf-8')
    lines = str_lines.split('\n')

    regex = re.compile(r'^\s*Device\s+Enabled\s+\(([0-9]+)\):\s+[01]$')

    pid = None  # property ID
    for line in lines:
        m = regex.match(line)
        if m is not None:
            pid = m.group(1)
            break

    ret = subprocess.run(
        ['xinput', '-set-prop', did, pid, '0'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main():
    _pre_flight_check()
    _take_off()


if __name__ == '__main__':
    main()
