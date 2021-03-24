

import os
import requests
from . import util


class Source:
    def get_script_location(self):
        raise NotImplementedError()

    def read_script(self):
        raise NotImplementedError()

    def compute_source(self, source_filename):
        raise NotImplementedError()

    def read_bytes(self, source_filename):
        raise NotImplementedError()

    def exists(self, source_filename):
        raise NotImplementedError()

    @staticmethod
    def new(script_location):
        if UrlScriptSource.is_url(script_location):
            return UrlScriptSource(script_location)
        elif LocalScriptSource.is_filename(script_location):
            return LocalScriptSource(script_location)
        else:
            raise ValueError("illegal script location")


class LocalScriptSource(Source):
    def __init__(self, script_filename):
        script_filename = util.remove_prefix(script_filename, 'file://')
        script_filename = os.path.abspath(script_filename)
        self.script_filename = script_filename
        self._script_dir = os.path.dirname(script_filename)

    def __str__(self):
        return self.script_filename

    def __repr__(self):
        return '{}(dir="{}")'.format(self.script_filename, self._script_dir)

    def get_script_location(self):
        return self.script_filename

    def read_script(self):
        with open(self.script_filename, 'rb') as f:
            return f.read().decode('utf-8')

    def compute_source(self, source_filename):
        if os.path.isabs(source_filename):
            raise ValueError("not support absolute filename")
        return os.path.abspath(os.path.join(self._script_dir, source_filename))

    def read_bytes(self, source_filename):
        filename = self.compute_source(source_filename)
        with open(filename, 'rb') as f:
            return f.read()

    def exists(self, source_filename):
        filename = self.compute_source(source_filename)
        return os.path.exists(filename)

    @staticmethod
    def is_filename(script_filename):
        if script_filename.startswith('file://'):
            return True
        if os.path.isabs(script_filename):
            return True
        return True


class UrlScriptSource(Source):
    def __init__(self, script_url):
        self.script_url, self._script_prefix, self._script_dir = self._strip_script_url(script_url)

    def __str__(self):
        return self.script_url

    def __repr__(self):
        return '{}(prefix="{}" dir="{}")'.format(self.script_url, self._script_prefix, self._script_dir)

    def get_script_location(self):
        return self.script_url

    def read_script(self):
        return requests.get(self.script_url).content

    def compute_source(self, source_filename):
        if os.path.isabs(source_filename):
            raise ValueError("not support absolute filename")
        fn = os.path.abspath(os.path.join(self._script_dir, source_filename))
        return self._script_prefix + fn

    def read_bytes(self, source_filename):
        url = self.compute_source(source_filename)
        return requests.get(url).content

    def exists(self, source_filename):
        url = self.compute_source(source_filename)
        return requests.head(url).status_code == 200

    @staticmethod
    def _strip_script_url(script_url):
        if script_url.startswith('http://'):
            return script_url, 'http:/', os.path.dirname(util.remove_prefix(script_url, 'http:/'))
        elif script_url.startswith('https://'):
            return script_url, 'https:/', os.path.dirname(util.remove_prefix(script_url, 'https:/'))
        else:
            raise ValueError("illegal script url")

    @staticmethod
    def is_url(script_url):
        return script_url.startswith('http://') or script_url.startswith('https://')





