
import os
import pathlib
import contextlib
import sys
import requests
from rich.console import Console

_stdout_console = Console(file=sys.stdout)
_stderr_console = Console(file=sys.stderr)


def remove_prefix(s, prefix):
    if not prefix:
        return s
    return s[len(prefix):] if s.startswith(prefix) else s


@contextlib.contextmanager
def work_in(work_dir):
    old_cwd = os.getcwd()
    try:
        os.chdir(work_dir)
        yield
    finally:
        os.chdir(old_cwd)


def mkdir_p(dirname):
    pathlib.Path(dirname).mkdir(parents=True, exist_ok=True)


def curl(url, as_text=True, strip=False):
    resp = None
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            raise Exception("illegal status code: {}".format(resp.status_code))
        if as_text:
            r = resp.text
            if strip:
                r = r.strip()
            return r
        else:
            return resp.content
    finally:
        if resp is not None:
            resp.close()



def console_log(msg):
    _stdout_console.print(msg)


def console_error(msg):
    _stderr_console.print(msg)
