from __future__ import annotations

import os
import sys

import click
from loguru import logger

from illuminate import __version__
from illuminate.common.project_logging import LOGGING_LEVELS
from illuminate.decorators.logging import show_observer_catalogue
from illuminate.manager.assistant import Assistant
from illuminate.manager.manager import Manager


@click.group()
@click.version_option(__version__)
@click.option(
    "--verbosity",
    default=LOGGING_LEVELS[2],
    help="Configure logging levels.",
    required=False,
    type=click.Choice(LOGGING_LEVELS),
    show_default=True,
)
@click.pass_context
def cli(ctx: dict, verbosity: str) -> None:
    """Framework entrypoint."""
    logger.remove()
    logger.add(sys.stdout, level=verbosity)
    sys.path.insert(0, os.getcwd())


@cli.group("manage")
@click.pass_context
def manage(ctx: dict) -> None:
    """Framework manage group of commands."""
    pass


@cli.group("observe")
@click.pass_context
def observe(ctx: dict) -> None:
    """Framework observe group of commands."""
    pass


@manage.group("db")
@click.pass_context
def db(ctx: dict) -> None:
    """Prepares relational db for ETL operations."""
    pass


@manage.group("project")
@click.pass_context
def project(ctx: dict) -> None:
    """Performs project operations."""
    pass


@db.command("populate")
@click.option(
    "--fixtures",
    help="Fixture files paths.",
    multiple=True,
    required=False,
    type=click.Path(exists=True),
)
@click.option(
    "--selector",
    default="main",
    help="Database connection selector.",
    required=False,
    show_default=True,
    type=str,
)
@click.option(
    "--url",
    default=None,
    help="Optional URL for databases not included in settings module.",
    required=False,
    type=str,
)
@click.pass_context
def db_populate(ctx: dict, selector: str, url: str, *args, **kwargs) -> None:
    """Populates database with fixtures."""
    kwargs["context"] = ctx
    Manager.db_populate(kwargs.pop("fixtures"), selector, url, *args, **kwargs)


@db.command("revision")
@click.option(
    "--revision",
    default="head",
    help="Alembic revision selector.",
    required=False,
    show_default=True,
    type=str,
)
@click.option(
    "--selector",
    default="main",
    help="Database connection selector.",
    required=False,
    show_default=True,
    type=str,
)
@click.option(
    "--url",
    default=None,
    help="Optional URL for databases not included in settings module.",
    required=False,
    type=str,
)
@click.argument(
    "path", default=os.getcwd(), required=False, type=click.Path(exists=True)
)
@click.pass_context
def db_revision(
    ctx: dict,
    path: str,
    revision: str,
    selector: str,
    url: str,
    *args,
    **kwargs
) -> None:
    """Creates Alembic's revision file in migration directory."""
    kwargs["context"] = ctx
    Manager.db_revision(path, revision, selector, url, *args, **kwargs)


@db.command("upgrade")
@click.option(
    "--revision",
    default="head",
    help="Alembic revision selector.",
    required=False,
    show_default=True,
    type=str,
)
@click.option(
    "--selector",
    default="main",
    help="Database connection selector.",
    required=False,
    show_default=True,
    type=str,
)
@click.option(
    "--url",
    default=None,
    help="Optional URL for databases not included in settings module.",
    required=False,
    type=str,
)
@click.argument(
    "path", default=os.getcwd(), required=False, type=click.Path(exists=True)
)
@click.pass_context
def db_upgrade(
    ctx: dict,
    path: str,
    revision: str,
    selector: str,
    url: str,
    *args,
    **kwargs
) -> None:
    """Applies migration file to a database."""
    kwargs["context"] = ctx
    Manager.db_upgrade(path, revision, selector, url, *args, **kwargs)


@project.command("setup")
@click.argument("name", required=True, type=str)
@click.argument(
    "path", default=os.getcwd(), required=False, type=click.Path(exists=True)
)
@click.pass_context
def setup(ctx: dict, name: str, path: str, *args, **kwargs) -> None:
    """Creates a project directory with all needed files."""
    kwargs["context"] = ctx
    Manager.project_setup(name, path, *args, **kwargs)


@observe.command("catalogue")
@click.pass_context
@show_observer_catalogue
def catalogue(ctx: dict, *args, **kwargs) -> dict:
    """Lists observers found in project files."""
    return Assistant.provide_context(sessions=False)


@observe.command("start")
@click.option(
    "--observer",
    help="Observer selector. Leave empty to include all observers.",
    multiple=True,
    required=False,
    type=str,
)
@click.pass_context
def start(ctx: dict, observer: tuple[str], *args, **kwargs) -> None:
    """Starts producer/consumer ETL process."""
    context = Assistant.provide_context(_filter=observer)
    manager = Manager(**context)  # type: ignore
    manager.observe_start()


if __name__ == "__main__":
    cli(obj={})
