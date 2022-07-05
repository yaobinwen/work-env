import contextlib
import pathlib
import shutil
import tempfile
import typing


@contextlib.contextmanager
def temp_dir(
    prefix: str="tmp.",
    tmpdir: typing.Union[str, pathlib.Path]="/tmp",
    delete: bool=True,
) -> pathlib.Path:
    d = tempfile.mkdtemp(prefix=prefix, dir=str(tmpdir))
    try:
        yield pathlib.Path(d)
    finally:
        if delete:
            shutil.rmtree(d, ignore_errors=True)
