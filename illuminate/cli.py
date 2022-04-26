import sys

import click

from illuminate import __version__


@click.group()
@click.version_option(__version__)
@click.pass_context
def cli():
    pass


@cli.group("manage")
@click.pass_context
def manage(ctx):
    """Framework manager"""
    pass


if __name__ == "__main__":
    cli(obj={})
