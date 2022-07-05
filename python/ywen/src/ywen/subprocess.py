import contextlib
import pathlib
import subprocess
import typing

from ywen import encoding


def run(
    *,
    cmd: typing.List[str],
    cwd: pathlib.Path,
    check: bool=False,
) -> typing.Tuple[int, str, str]:
    cp = subprocess.run(
        args=cmd,
        cwd=cwd,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        check=check,
    )

    stdout_str = cp.stdout.decode(encoding.PREFERRED_ENCODING)
    stderr_str = cp.stderr.decode(encoding.PREFERRED_ENCODING)

    if cp.returncode != 0:
        raise subprocess.CalledProcessError(
            f"Command '{cmd}' returned non-zero exit status {cp.returncode}: "
            f"{stderr_str}"
        )

    return cp.returncode, stdout_str, stderr_str


@contextlib.contextmanager
def run_query_stdout(
    *,
    cmd: typing.List[str],
    cwd: pathlib.Path,
    check: bool=False,
) -> int:
    p = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, cwd=cwd
    )

    try:
        yield p.stdout
        rc = p.wait()
        if check and rc != 0:
            stderr_str = p.stderr.decode(encoding.PREFERRED_ENCODING)
            raise subprocess.CalledProcessError(
                f"Command '{cmd}' "
                f"returned non-zero exit status {p.returncode}: "
                f"{stderr_str}"
            )
    finally:
        p.stdout.close()

    return p.returncode
