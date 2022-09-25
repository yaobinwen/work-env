# standard
import pathlib
import unittest

# ours
from ywen import (
    encoding,
    tempfile,
    subprocess,
)

class TestImport(unittest.TestCase):
    def test_import(self):
        import ywen.subprocess


_HELLO = "hello, world!"
_PREFIX = pathlib.Path(__file__).name

_SCRIPT = """
#!/bin/sh

read MSG
read SLEEP
sleep $SLEEP
echo "The message is: $MSG"
""".strip()


class Test_run(unittest.TestCase):
    def test_cmd(self):
        _, stdout_str, _ = subprocess.run(
            cmd=[
                "echo",
                _HELLO,
            ],
        )

        stdout_lines = stdout_str.splitlines()
        self.assertEqual(len(stdout_lines), 1)
        self.assertEqual(stdout_lines[0], _HELLO)

    def test_cwd(self):
        with tempfile.temp_dir(prefix=_PREFIX) as tmp_dir:
            _, stdout_str, _ = subprocess.run(
                cmd=[
                    "pwd",
                ],
                cwd=tmp_dir,
            )

            stdout_lines = stdout_str.splitlines()
            self.assertEqual(len(stdout_lines), 1)
            self.assertEqual(stdout_lines[0], str(tmp_dir))

    def test_input_no_timeout(self):
        with tempfile.temp_dir(prefix=_PREFIX) as tmp_dir:
            script_fpath = tmp_dir / "test_input.sh"
            script_fpath.write_text(
                data=_SCRIPT,
                encoding=encoding.PREFERRED_ENCODING,
            )
            script_fpath.chmod(mode=0o755)

            _, stdout_str, _ = subprocess.run(
                cmd=[
                    str(script_fpath),
                ],
                input="hello\n0\n",
                cwd=tmp_dir,
            )

            stdout_lines = stdout_str.splitlines()
            self.assertEqual(len(stdout_lines), 1)
            self.assertEqual(stdout_lines[0], "The message is: hello")

    def test_input_with_timeout(self):
        with tempfile.temp_dir(prefix=_PREFIX) as tmp_dir:
            script_fpath = tmp_dir / "test_input.sh"
            script_fpath.write_text(
                data=_SCRIPT,
                encoding=encoding.PREFERRED_ENCODING,
            )
            script_fpath.chmod(mode=0o755)

            self.assertRaises(
                subprocess.TimeoutExpired,
                subprocess.run,
                cmd=[
                    str(script_fpath),
                ],
                input="hello\n2\n",
                input_timeout=0.5,
                cwd=tmp_dir,
            )

    def test_no_encoding(self):
        _, stdout_bytes, _ = subprocess.run(
            cmd=[
                "echo",
                _HELLO,
            ],
            encoding=None,
        )

        self.assertIsInstance(stdout_bytes, bytes)

        stdout_str = stdout_bytes.decode(encoding.PREFERRED_ENCODING)
        stdout_lines = stdout_str.splitlines()
        self.assertEqual(len(stdout_lines), 1)
        self.assertEqual(stdout_lines[0], _HELLO)

    def test_no_check(self):
        rc, _, _ = subprocess.run(
            cmd=[
                "false",
            ],
            check=False,    # no error will be raised
        )
        self.assertTrue(rc != 0)

    def test_err_return_code(self):
        self.assertRaises(
            subprocess.CalledProcessError,
            subprocess.run,
            cmd=[
                "false",
            ],
            check=True,
        )


_SCRIPT_LONG_OUTPUT = """
#!/bin/sh

echo "output line 1"
for i in $(seq 2 3); do
    sleep 1
    echo "output line $i"
done
""".strip()


class Test_run_query_stdout(unittest.TestCase):
    def test_cmd(self):
        with subprocess.run_query_stdout(
            cmd=[
                "echo",
                _HELLO,
            ],
        ) as q:
            stdout_str = q.read()
            stdout_lines = stdout_str.splitlines()
            self.assertEqual(len(stdout_lines), 1)
            self.assertEqual(stdout_lines[0], _HELLO)

    def test_long_output(self):
        with tempfile.temp_dir(prefix=_PREFIX) as tmp_dir:
            script_fpath = tmp_dir / "test_long_output.sh"
            script_fpath.write_text(
                data=_SCRIPT_LONG_OUTPUT,
                encoding=encoding.PREFERRED_ENCODING,
            )
            script_fpath.chmod(mode=0o755)

            with subprocess.run_query_stdout(
                cmd=[
                    str(script_fpath),
                ],
            ) as q:
                stdout_str = q.read()
                stdout_lines = stdout_str.splitlines()
                self.assertEqual(len(stdout_lines), 3)

                for i in range(0, len(stdout_lines)):
                    self.assertEqual(stdout_lines[i], f"output line {i+1}")

    def test_cwd(self):
        with tempfile.temp_dir(prefix=_PREFIX) as tmp_dir:
            with subprocess.run_query_stdout(
                cmd=[
                    "pwd",
                ],
                cwd=tmp_dir,
            ) as q:
                stdout_str = q.read()
                stdout_lines = stdout_str.splitlines()
                self.assertEqual(len(stdout_lines), 1)
                self.assertEqual(stdout_lines[0], str(tmp_dir))

    def test_no_encoding(self):
        with subprocess.run_query_stdout(
            cmd=[
                "echo",
                _HELLO,
            ],
            encoding=None,
        ) as q:
            stdout_bytes = q.read()
            self.assertIsInstance(stdout_bytes, bytes)

            stdout_str = stdout_bytes.decode(encoding.PREFERRED_ENCODING)
            stdout_lines = stdout_str.splitlines()
            self.assertEqual(len(stdout_lines), 1)
            self.assertEqual(stdout_lines[0], _HELLO)

    def test_err_return_code(self):
        try:
            with subprocess.run_query_stdout(
                cmd=[
                    "false",
                ],
                check=True,
            ) as q:
                pass
            self.fail("'CalledProcessError' is expected but not raised")
        except subprocess.CalledProcessError as ex:
            pass
