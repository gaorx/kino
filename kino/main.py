import os
import click

from .source import Source
from .context import Context
from . import util


@click.command('kino', context_settings={'ignore_unknown_options': True}, add_help_option=False)
@click.option('-h', '--help', is_flag=True, expose_value=False, help="Show this message and exit", is_eager=True,
              callback=util.click_show_help)
@click.option('-t', '--target', default='', help="Target directory")
@click.option('--overwrite', is_flag=True, default=False, help="allow overwrite target file", show_default=True)
@click.argument('source_location')
@click.argument('source_args', nargs=-1, type=click.UNPROCESSED)
def main(target, source_location, source_args, overwrite):
    target = os.path.abspath(target)
    if not os.path.exists(target):
        util.mkdir_p(target)
    source = Source.new(source_location)
    Context(target, source, source_args, allow_overwrite=overwrite).run_py(source.read_script())
