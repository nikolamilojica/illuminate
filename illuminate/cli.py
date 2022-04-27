import os

import click

from illuminate import __version__
from illuminate.manager.manager import Manager


@click.group()
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    pass


@cli.group("manage")
@click.pass_context
def manage(ctx):
    """Framework manager"""
    pass


@manage.command("setup")
@click.argument("name", required=True)
@click.argument("path", default=os.getcwd(), required=False)
@click.pass_context
def setup(ctx, name, path, *args, **kwargs):
    """Creates project structure with example files"""
    kwargs["context"] = ctx
    Manager.setup(name, path, *args, **kwargs)


if __name__ == "__main__":
    cli(obj={})
