import json
import os
import shutil

import click
import jinja2

from . import util


class Context:
    class Proxy:
        def __init__(self, context):
            self.context = context

        def __getattr__(self, item):
            if item.startswith('_') or item in ['run', 'run_py']:
                return None
            return getattr(self.context, item)

    def __init__(self, target_dir, source, source_args, allow_overwrite=False):
        target_dir = os.path.abspath(target_dir)
        if not os.path.isdir(target_dir):
            raise ValueError("target directory error")
        self._target_dir = target_dir
        self._source = source
        self._source_args = list(source_args)
        self._allow_overwrite = allow_overwrite

    def run(self, f):
        with util.work_in(self._target_dir):
            f(Context.Proxy(self))

    def run_py(self, py_source):
        scope = {}
        exec(py_source, scope, scope)
        main_fn = scope.get('main')
        if not callable(main_fn):
            raise Exception("no main function in kino script file")
        with util.work_in(self._target_dir):
            main_fn(Context.Proxy(self))

    def _write_bytes(self, filename, data, mkdir=False):
        filename = os.path.abspath(filename)
        if not self._allow_overwrite:
            if os.path.exists(filename):
                raise util.KinoError("overwrite {}, use --overwrite option".format(filename))
        if mkdir:
            util.mkdir_p(os.path.dirname(filename))

        with open(filename, 'wb') as f:
            f.write(data)

    def _log_action(self, verb, obj):
        self.log("[green]{}[/green] {}", verb, obj)

    # properties

    @property
    def target_dir(self):
        return self._target_dir

    @property
    def source_args(self):
        return self._source_args

    @property
    def target_name(self):
        return os.path.basename(self._target_dir)

    @staticmethod
    def raise_error(msg):
        raise util.KinoError(msg)

    # import

    def import_(self, source_script):
        def import_one(s):
            py = self.read_source(s)
            scope = {}
            exec(py, scope, scope)
            return util.AttrDict(**scope)
        if isinstance(source_script, str):
            return import_one(source_script)
        else:
            return tuple(map(import_one, list(source_script)))

    # log

    @staticmethod
    def log(msg, *args, **kwargs):
        util.console_log(msg.format(*args, **kwargs))

    @staticmethod
    def log_error(msg, *args, **kwargs):
        util.console_error(msg.format(*args, **kwargs))

    # args

    @staticmethod
    def option(*param_decls, **attrs):
        return click.option(*param_decls, **attrs)

    @staticmethod
    def argument(*param_decls, **attrs):
        return click.argument(*param_decls, **attrs)

    def get_args(self, args_spec):
        def f(**kwargs):
            kwargs = kwargs.copy()
            if 'target_name' not in kwargs:
                kwargs['target_name'] = self.target_name
            return util.AttrDict(**kwargs)

        for arg_spec in reversed(args_spec):
            f = arg_spec(f)
        f = click.option('-H', '--HELP', is_flag=True, expose_value=False,
                         help="Show this message and exit", is_eager=True, callback=util.click_show_help)(f)
        f = click.command(add_help_option=False)(f)
        ctx = f.make_context("kino script", self._source_args)
        return f.invoke(ctx)

    # source

    def exists_source(self, source):
        return self._source.exists(source)

    def read_source(self, source, as_text=True, encoding='utf-8'):
        data = self._source.read_bytes(source)
        return data.decode(encoding) if as_text else data

    # target

    def mkdir(self, dirname):
        util.mkdir_p(dirname)
        self._log_action('mkdir', dirname)

    def copy(self, filename, source=None, mkdir=True):
        if not source:
            source = filename
        content = self._source.read_bytes(source)
        self._write_bytes(filename, content, mkdir=mkdir)
        if source == filename:
            self._log_action('copy ', filename)
        else:
            self._log_action('copy ', '{} <- {}'.format(filename, source))

    def write(self, filename, content=None, source=None, args=None, mkdir=True, content_encoding='utf-8'):
        if content is not None:
            if isinstance(content, bytes):
                pass
            elif isinstance(content, str):
                content = content.encode(content_encoding)
            else:
                raise ValueError("illegal content type")
        elif source is not None:
            content = self._source.read_bytes(source)
        else:
            raise ValueError("no content/source")

        if args is not None:
            content_text = content.decode('utf-8')
            content = jinja2.Template(content_text).render(**args).encode(content_encoding)
        self._write_bytes(filename, content, mkdir=mkdir)
        self.log("[green]write[/green] {}", filename)

    def download(self, filename, url, mkdir=True):
        data = util.curl(url, as_text=False, strip=False)
        self._write_bytes(filename, data, mkdir=mkdir)

    def wget(self, filename, url, mkdir=True):
        self.download(filename, url, mkdir=mkdir)

    @staticmethod
    def exists(filename):
        return os.path.exists(filename)

    @staticmethod
    def read(filename, as_text=True, encoding='utf-8'):
        with open(filename, 'rb') as f:
            data = f.read()
            return data.decode(encoding) if as_text else data

    @staticmethod
    def rm(filename):
        if os.path.exists(filename):
            if os.path.isdir(filename):
                shutil.rmtree(filename)
            else:
                os.remove(filename)

    # tools

    @staticmethod
    def work_in(wd):
        return util.work_in(wd)

    @staticmethod
    def to_json(value, pretty=True, sort_keys=False):
        if pretty:
            return json.dumps(value, indent='  ', sort_keys=sort_keys)
        else:
            return json.dumps(value)

    @staticmethod
    def curl(url, as_text=True, strip=False):
        return util.curl(url, as_text=as_text, strip=strip)

    @staticmethod
    def curl_gitignore(lang, mac_os=True, intellij_idea=True, vscode=True, netbeans=True, other=''):
        if not lang:
            raise ValueError("no language for .gitignore")
        from . import gitignore
        gitignore_url = 'https://raw.githubusercontent.com/github/gitignore/master/{}.gitignore'.format(lang)
        r = util.curl(gitignore_url)
        if mac_os:
            r += gitignore.macos
        if intellij_idea:
            r += gitignore.intellij_idea
        if vscode:
            r += gitignore.vscode
        if netbeans:
            r += gitignore.netbeans
        if other:
            r += '\n' + other + '\n'
        return r
