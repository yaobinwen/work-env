import contextlib
import pathlib
import subprocess
import typing

from ywen.encoding import PREFERRED_ENCODING


def run(
    *,
    cmd: typing.List[str],
    input: str=None,
    input_timeout: float=None,
    stderr: int=subprocess.PIPE,
    stdout: int=subprocess.PIPE,
    encoding: str=PREFERRED_ENCODING,
    cwd: pathlib.Path=None,
    check: bool=False,
) -> typing.Tuple[int, str, str]:
    cp = subprocess.run(
        args=cmd,
        input=input,
        timeout=input_timeout,
        stderr=stderr,
        stdout=stdout,
        encoding=encoding,
        cwd=cwd,
        check=check,
    )

    return cp.returncode, cp.stdout, cp.stderr


@contextlib.contextmanager
def run_query_stdout(
    *,
    cmd: typing.List[str],
    stderr: int=subprocess.PIPE,
    stdout: int=subprocess.PIPE,
    encoding: str=PREFERRED_ENCODING,
    cwd: pathlib.Path=None,
    check: bool=False,
) -> int:
    p = subprocess.Popen(
        cmd,
        stderr=stderr,
        stdout=stdout,
        encoding=encoding,
        cwd=cwd,
    )

    try:
        yield p.stdout
        rc = p.wait()
        if check and rc != 0:
            raise subprocess.CalledProcessError(
                returncode=p.returncode,
                cmd=cmd,
                stderr=p.stderr,
            )
    finally:
        p.stdout.close()


CalledProcessError = subprocess.CalledProcessError
TimeoutExpired = subprocess.TimeoutExpired
