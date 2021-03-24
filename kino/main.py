import os
import click

from .source import Source
from .context import Context
from . import util


@click.command('kino', context_settings={'ignore_unknown_options': True})
@click.option('-t', '--target', default='')
@click.argument('source_location')
@click.argument('source_args', nargs=-1)
def main(target, source_location, source_args):
    target = os.path.abspath(target)
    if not os.path.exists(target):
        util.mkdir_p(target)
    source = Source.new(source_location)
    Context(target, source).run_py(source.read_script())
