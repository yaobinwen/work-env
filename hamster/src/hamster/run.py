# -*- coding: utf-8 -*-

import logging
import subprocess
from pathlib import PurePath


loggerName = PurePath(PurePath(__file__).name).stem
logger = logging.getLogger(loggerName)


def run(cmd, cwd, timeout=None):
    logger.debug(f"cmd={cmd}; cwd={cwd}; timeout={timeout}")

    ret = subprocess.run(
        cmd,
        cwd=cwd,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )

    try:
        ret.check_returncode()
        logger.debug(f"ret={ret}")
    except Exception as ex:
        logger.exception(f"{str(ex)} stderr: {ret.stderr}")
        raise

    return ret
