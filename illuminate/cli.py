import os

import click

from illuminate import __version__
from illuminate.manager.manager import Assistant
from illuminate.manager.manager import Manager


@click.group()
@click.version_option(__version__)
@click.pass_context
def cli(ctx):
    pass


@cli.group("manage")
@click.pass_context
def manage(ctx):
    """Framework manage group of commands"""
    pass


@cli.group("observe")
@click.pass_context
def observe(ctx):
    """Framework observe group of commands"""
    pass


@manage.group("db")
@click.pass_context
def db(ctx):
    """Prepares relational db for ETL operations"""
    pass


@manage.group("project")
@click.pass_context
def project(ctx):
    """Performs project operations"""
    pass


@db.command("populate")
@click.option("--selector", default="main", required=False)
@click.option("--fixtures", multiple=True, required=False, type=click.Path(exists=True))
@click.argument("url", default=None, required=False)
@click.pass_context
def db_populate(ctx, selector, url, *args, **kwargs):
    """Populate db with fixtures"""
    kwargs["context"] = ctx
    Manager.db_populate(kwargs.pop("fixtures"), selector, url, *args, **kwargs)


@db.command("revision")
@click.option("--selector", default="main", required=False)
@click.option("--revision", default="head", required=True)
@click.argument("url", default=None, required=False)
@click.argument("path", default=os.getcwd(), required=False)
@click.pass_context
def db_revision(ctx, path, revision, selector, url, *args, **kwargs):
    """Creates revision files"""
    kwargs["context"] = ctx
    Manager.db_revision(path, revision, selector, url, *args, **kwargs)


@db.command("upgrade")
@click.option("--selector", default="main", required=False)
@click.option("--revision", default="head", required=True)
@click.argument("url", default=None, required=False)
@click.argument("path", default=os.getcwd(), required=False)
@click.pass_context
def db_upgrade(ctx, path, revision, selector, url, *args, **kwargs):
    """Performs migration based on revision files"""
    kwargs["context"] = ctx
    Manager.db_upgrade(path, revision, selector, url, *args, **kwargs)


@project.command("setup")
@click.argument("name", required=True, type=str)
@click.argument("path", default=os.getcwd(), required=False)
@click.pass_context
def setup(ctx, name, path, *args, **kwargs):
    """Creates project structure with example files"""
    kwargs["context"] = ctx
    Manager.project_setup(name, path, *args, **kwargs)


@observe.command("start")
@click.pass_context
def start(ctx, *args, **kwargs):
    """Start producer/consumer ETL process based on project files"""
    kwargs["context"] = ctx
    context = Assistant.provide_context()
    manager = Manager(**context)
    manager.observe_start()


if __name__ == "__main__":
    cli(obj={})
