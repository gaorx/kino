
import os
import json
import jinja2
import requests

from . import util


class Context:
    class Proxy:
        def __init__(self, context):
            self.context = context

        def __getattr__(self, item):
            if item.startswith('_') or item in ['run', 'run_py']:
                return None
            return getattr(self.context, item)

    def __init__(self, target_dir, source):
        target_dir = os.path.abspath(target_dir)
        if not os.path.isdir(target_dir):
            raise ValueError("target directory error")
        self.target_dir = target_dir
        self.source = source

    def run(self, f):
        with util.work_in(self.target_dir):
            f(Context.Proxy(self))

    def run_py(self, py_source):
        scope = {}
        exec(py_source, scope, scope)
        main_fn = scope.get('main')
        if not callable(main_fn):
            raise Exception("no main function in kino script file")
        with util.work_in(self.target_dir):
            main_fn(Context.Proxy(self))

    @staticmethod
    def _write_bytes(filename, data, mkdir=False):
        filename = os.path.abspath(filename)
        if mkdir:
            util.mkdir_p(os.path.dirname(filename))

        with open(filename, 'wb') as f:
            f.write(data)

    @staticmethod
    def log(msg, *args, **kwargs):
        util.console_log(msg.format(*args, **kwargs))

    @staticmethod
    def log_error(msg, *args, **kwargs):
        util.console_error(msg.format(*args, **kwargs))

    @staticmethod
    def work_in(wd):
        return util.work_in(wd)

    @staticmethod
    def mkdir_p(dirname):
        util.mkdir_p(dirname)

    def copy(self, filename, source=None, mkdir=True):
        if not source:
            source = filename
        content = self.source.read_bytes(source)
        self._write_bytes(filename, content, mkdir=mkdir)
        if source == filename:
            self.log("[green]copy[/green] {}", filename)
        else:
            self.log("[green]copy[/green] {} <- {}", filename, source)

    def write(self, filename, content=None, source=None, args=None, mkdir=True, content_encoding='utf-8'):
        if content is not None:
            if isinstance(content, bytes):
                pass
            elif isinstance(content, str):
                content = content.encode(content_encoding)
            else:
                raise ValueError("illegal content type")
        elif source is not None:
            content = self.source.read_bytes(source)
        else:
            raise ValueError("no content/source")

        if args is not None:
            content_text = content.decode('utf-8')
            content = jinja2.Template(content_text).render(**args).encode(content_encoding)
        self._write_bytes(filename, content, mkdir=mkdir)
        self.log("[green]write[/green] {}", filename)

    @staticmethod
    def exists(filename):
        return os.path.exists(filename)

    def exists_source(self, source):
        return self.source.exists(source)

    @staticmethod
    def to_json(value, pretty=True, sort_keys=False):
        if pretty:
            return json.dumps(value, indent='  ', sort_keys=sort_keys)
        else:
            return json.dumps(value)

    @staticmethod
    def curl(url, as_text=True, strip=False):
        return util.curl(url, as_text=as_text, strip=strip)




