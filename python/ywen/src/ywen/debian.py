import pathlib
import re
import typing

from ywen import subprocess


REGEX_MAINTAINER_VALUE = re.compile(
    r"^([\w\d\s]+)\s\<([\w\d\s\-\._]+\@[\w\d\-_]+\.[\w\d]+)\>$"
)

_REGEX_VERSION = r"(\d+\.\d+\.\d+)\-([\w\d\+\.\~]+)"

# Ref: https://www.debian.org/doc/debian-policy/ch-controlfields.html#version
# Note the difference between the policy and my implementation:
# - 1). I don't use the epoch version (or I always use the default value `0`).
# - 2). Debian version allows a more flexible format for `upstream_version`
# but I think I'll keep using semantic version core format (major.minor.patch)
# to make things easier.
REGEX_VERSION_VALUE = re.compile(rf"^{_REGEX_VERSION}$")

# Example: "abc (0.2.0-1) UNRELEASED; urgency=low"
REGEX_ENTRY_HEADER_VALUE = re.compile(
    rf"^([\w\d\-_]+)\s\({_REGEX_VERSION}\)\s([\w\d]+);\surgency=(\w+)$"
)


def _changelog_field(
    *,
    changelog: pathlib.Path,
    field: str,
    all_changes: bool=False,
):
    cmd = [
        "dpkg-parsechangelog",
        "--file",
        str(changelog),
        "--show-field",
        field,
    ]
    if all_changes:
        # NOTE(ywen): If we insert `--all` with the code
        # `"--all" if all_changes else ""`, an empty string `""` is passed to
        # `dpkg-parsechangelog` and causes the error "takes no non-option
        # arguments".
        cmd.append("--all")

    _, stdout_str, _ = subprocess.run(cmd=cmd)

    return stdout_str.rstrip("\n")


_original_value = lambda v: v


class Maintainer(object):
    def __init__(
        self, *,
        name: str,
        email: str,
    ):
        self.name = name
        self.email = email

    @staticmethod
    def from_str(value: str) -> "Maintainer":
        m = REGEX_MAINTAINER_VALUE.match(value)
        if m is None:
            raise ValueError(
                f"'{value}' does not match the maintainer format."
            )

        return Maintainer(name=m.group(1), email=m.group(2))


class Version(object):
    def __init__(
        self, *,
        epoch: str="0",
        upstream: str,
        debian: str,
    ):
        self.epoch = epoch
        self.upstream = upstream
        self.debian = debian

    @staticmethod
    def from_str(value: str) -> "Version":
        m = REGEX_VERSION_VALUE.match(value)
        if m is None:
            raise ValueError(
                f"'{value}' does not match the version format."
            )

        return Version(epoch="0", upstream=m.group(1), debian=m.group(2))


class ChangeEntry(object):
    def __init__(
        self, *,
        source: str,
        version: Version,
        distribution: str,
        urgency: str,
        details: str,
    ):
        self.source = source
        self.version = version
        self.distribution = distribution
        self.urgency = urgency
        self.details = details


class Changes(object):
    def __init__(
        self, *,
        changes: typing.List[ChangeEntry],
    ):
        self.changes = changes

    @staticmethod
    def from_str(lines: str) -> "Changes":
        changes = []

        in_entry = False
        details = ""
        current_header_match = None
        for line in lines.splitlines():
            line = line.strip()
            if not line:
                continue

            m = REGEX_ENTRY_HEADER_VALUE.match(line)
            if m is None:
                # Not a header line.
                if in_entry:
                    # This must be a detailed line of the current change entry.
                    details += line
                else:
                    raise ValueError(
                        f"The line is not in any change entry: {line}"
                    )
            else:
                # Is a header line.
                current_header_match = m
                if in_entry:
                    # We need to close the previous entry.
                    change = ChangeEntry(
                        source=m.group(1),
                        version=Version(upstream=m.group(2), debian=m.group(3)),
                        distribution=m.group(4),
                        urgency=m.group(5),
                        details=details,
                    )
                    changes.append(change)
                else:
                    # This must be the first entry in changelog so we set
                    # `in_entry` to `True`.
                    in_entry = True

        change = ChangeEntry(
            source=current_header_match.group(1),
            version=Version(
                upstream=current_header_match.group(2),
                debian=current_header_match.group(3),
            ),
            distribution=current_header_match.group(4),
            urgency=current_header_match.group(5),
            details=details,
        )
        changes.append(change)

        return Changes(changes=changes)


_CHANGELOG_FIELDS = {
    "Changes": Changes.from_str,
    "Date": _original_value,
    "Distribution": _original_value,
    "Maintainer": Maintainer.from_str,
    "Source": _original_value,
    "Timestamp": int,
    "Urgency": _original_value,
    "Version": Version.from_str,
}


class Changelog(object):
    def __init__(
        self, *,
        changelog: pathlib.Path,
        all_changes: bool=False,
    ):
        for field, handler in _CHANGELOG_FIELDS.items():
            value = _changelog_field(
                changelog=changelog,
                field=field,
                all_changes=all_changes,
            )
            setattr(self, field, handler(value))
