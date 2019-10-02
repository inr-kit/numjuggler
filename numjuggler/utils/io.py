import os
from .resource import Path
from contextlib import contextmanager


@contextmanager
def cd_temporarily(cd_to):
    cur_dir = str(Path.cwd())
    try:
        os.chdir(str(cd_to))
        yield
    finally:
        os.chdir(cur_dir)
