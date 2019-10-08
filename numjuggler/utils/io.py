import os
import sys

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


@contextmanager
def resolve_fname_or_stream(fname_or_stream, mode="r"):
    is_input = mode == 'r'
    if fname_or_stream is None:
        if is_input:
            yield sys.stdin
        else:
            yield sys.stdout
    elif is_input and hasattr(fname_or_stream, "read") or not is_input and hasattr(fname_or_stream, "write"):
        yield fname_or_stream
    else:
        with open(fname_or_stream, mode=mode) as fid:
            yield fid
