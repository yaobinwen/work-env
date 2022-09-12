from multiprocessing.sharedctypes import Value
import unittest

from ywen.encoding import PREFERRED_ENCODING
from ywen.debian import (
    Changelog,
    Maintainer,
    Version,
)
from ywen.tempfile import temp_dir


class TestImport(unittest.TestCase):
    def test_import(self):
        import ywen.debian


class TestMaintainer(unittest.TestCase):
    def test_init(self):
        name = "John Doe"
        email = "john.doe@gmail.com"
        m = Maintainer(
            name=name,
            email=email,
        )
        self.assertEqual(m.name, name)
        self.assertEqual(m.email, email)

    def test_from_str_success(self):
        name = "John Doe"
        email = "john.doe@gmail.com"
        m = Maintainer.from_str(f"{name} <{email}>")
        self.assertEqual(m.name, name)
        self.assertEqual(m.email, email)

    def test_from_str_failure(self):
        name = "John Doe"
        email = "john.doe@gmail.com"
        self.assertRaises(
            ValueError,
            Maintainer.from_str,
            value=f"{name} - {email}",
        )


class TestVersion(unittest.TestCase):
    def test_init(self):
        epoch = "1"
        upstream = "1.2.3"
        debian = "1"
        v = Version(epoch=epoch, upstream=upstream, debian=debian)
        self.assertEqual(v.epoch, epoch)
        self.assertEqual(v.upstream, upstream)
        self.assertEqual(v.debian, debian)

    def test_from_str_success(self):
        epoch = "0"
        upstream = "1.2.3"
        debian = "1"
        v = Version.from_str(f"{upstream}-{debian}")
        self.assertEqual(v.epoch, epoch)
        self.assertEqual(v.upstream, upstream)
        self.assertEqual(v.debian, debian)

    def test_from_str_failure(self):
        self.assertRaises(
            ValueError,
            Version.from_str,
            value="abc",
        )


_TEST_CHANGELOG = """
abc (0.2.0-1) UNRELEASED; urgency=low

  * Release 0.2.0.

 -- Yaobin Wen <robin.wyb@gmail.com>  Tue, 05 Jul 2022 11:34:39 -0400

abc (0.1.0-1) UNRELEASED; urgency=high

  * Release 0.1.0.

 -- Yaobin Wen <robin.wyb@gmail.com>  Tue, 05 Jul 2022 10:52:15 -0400
""".strip("\n")


_TEST_CHANGELOG_WRONG_HEADER_FORMAT = """
abc (0.1-1) UNRELEASED; urgency=high

  * Release 0.1.

 -- Yaobin Wen <robin.wyb@gmail.com>  Tue, 05 Jul 2022 10:52:15 -0400
"""

_TEST_CHANGELOG_MISSING_HEADER = """
  * Release 0.1.

 -- Yaobin Wen <robin.wyb@gmail.com>  Tue, 05 Jul 2022 10:52:15 -0400
"""


class TestParsing(unittest.TestCase):
    def test_parsing_all(self):
        with temp_dir(prefix="debian.", delete=False) as d:
            changelog = d / "changelog"
            with changelog.open(
                mode="w",
                encoding=PREFERRED_ENCODING,
            ) as fh:
                fh.write(_TEST_CHANGELOG)

            c = Changelog(changelog=changelog, all_changes=True)

            self.assertEqual(len(c.Changes.changes), 2)

            self.assertEqual(c.Date, "Tue, 05 Jul 2022 11:34:39 -0400")
            self.assertEqual(c.Distribution, "UNRELEASED")
            self.assertEqual(c.Maintainer.name, "Yaobin Wen")
            self.assertEqual(c.Maintainer.email, "robin.wyb@gmail.com")
            self.assertEqual(c.Source, "abc")

            # Assume the timestamp is correctly calculated from the date by
            # `dpkg-parsechangelog`.
            self.assertGreater(c.Timestamp, 0)

            # Urgency is the highest one when all the change entries are
            # parsed.
            self.assertEqual(c.Urgency, "high")
            self.assertEqual(c.Version.epoch, "0")
            self.assertEqual(c.Version.upstream, "0.2.0")
            self.assertEqual(c.Version.debian, "1")

    def test_parsing_latest(self):
        with temp_dir(prefix="debian.", delete=False) as d:
            changelog = d / "changelog"
            with changelog.open(
                mode="w",
                encoding=PREFERRED_ENCODING,
            ) as fh:
                fh.write(_TEST_CHANGELOG)

            c = Changelog(changelog=changelog, all_changes=False)

            self.assertEqual(len(c.Changes.changes), 1)

            self.assertEqual(c.Date, "Tue, 05 Jul 2022 11:34:39 -0400")
            self.assertEqual(c.Distribution, "UNRELEASED")
            self.assertEqual(c.Maintainer.name, "Yaobin Wen")
            self.assertEqual(c.Maintainer.email, "robin.wyb@gmail.com")
            self.assertEqual(c.Source, "abc")

            # Assume the timestamp is correctly calculated from the date by
            # `dpkg-parsechangelog`.
            self.assertGreater(c.Timestamp, 0)

            self.assertEqual(c.Urgency, "low")
            self.assertEqual(c.Version.epoch, "0")
            self.assertEqual(c.Version.upstream, "0.2.0")
            self.assertEqual(c.Version.debian, "1")

    def test_header_line_wrong_format(self):
        with temp_dir(prefix="debian.", delete=False) as d:
            changelog = d / "changelog"
            with changelog.open(
                mode="w",
                encoding=PREFERRED_ENCODING,
            ) as fh:
                fh.write(_TEST_CHANGELOG_WRONG_HEADER_FORMAT)

            try:
                c = Changelog(changelog=changelog, all_changes=False)
            except ValueError as ex:
                msg = str(ex)
                self.assertIn("looks like a change entry header", msg)
                self.assertIn("does not match the expected format", msg)

    def test_missing_header_line(self):
        with temp_dir(prefix="debian.", delete=False) as d:
            changelog = d / "changelog"
            with changelog.open(
                mode="w",
                encoding=PREFERRED_ENCODING,
            ) as fh:
                fh.write(_TEST_CHANGELOG_MISSING_HEADER)

            try:
                c = Changelog(changelog=changelog, all_changes=False)
            except ValueError as ex:
                msg = str(ex)
                self.assertIn("The line is not in any change entry", msg)
