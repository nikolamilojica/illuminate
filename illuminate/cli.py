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


@manage.command("db")
@click.option("--selector", default="main", required=False)
@click.argument(
    "action",
    required=True,
    type=click.Choice(("upgrade", "revision"), case_sensitive=False),
)
@click.argument("revision", default="head", required=True)
@click.argument("url", default=None, required=False)
@click.argument("path", default=os.getcwd(), required=False)
@click.pass_context
def db(ctx, action, path, revision, selector, url, *args, **kwargs):
    """Prepare db for ETL"""
    kwargs["context"] = ctx
    Manager.db(action, path, revision, selector, url, *args, **kwargs)


@manage.command("setup")
@click.argument("name", required=True, type=str)
@click.argument("path", default=os.getcwd(), required=False)
@click.pass_context
def setup(ctx, name, path, *args, **kwargs):
    """Creates project structure with example files"""
    kwargs["context"] = ctx
    Manager.setup(name, path, *args, **kwargs)


if __name__ == "__main__":
    cli(obj={})
