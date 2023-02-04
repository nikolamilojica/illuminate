from __future__ import annotations

import os
import sys
import warnings

import click
from loguru import logger

from illuminate import __version__
from illuminate.common import LOGGING_LEVELS
from illuminate.manager import Assistant
from illuminate.manager import Manager


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
def cli(verbosity: str) -> None:
    """Framework entrypoint."""
    logger.remove()
    logger.add(sys.stdout, level=verbosity)
    sys.path.insert(0, os.getcwd())
    if not sys.warnoptions:
        warnings.simplefilter("ignore")


@cli.group("manage")
def manage() -> None:
    """Framework manage group of commands."""
    pass


@cli.group("observe")
def observe() -> None:
    """Framework observe group of commands."""
    pass


@manage.group("db")
def db() -> None:
    """Prepares relational db for ETL operations."""
    pass


@manage.group("project")
def project() -> None:
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
def db_populate(fixtures: tuple[str], selector: str, url: str) -> None:
    """Populates database with fixtures."""
    Manager.db_populate(fixtures, selector, url)


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
def db_revision(
    path: str,
    revision: str,
    selector: str,
    url: str,
) -> None:
    """Creates Alembic's revision file in migration directory."""
    Manager.db_revision(path, revision, selector, url)


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
def db_upgrade(
    path: str,
    revision: str,
    selector: str,
    url: str,
) -> None:
    """Applies migration file to a database."""
    Manager.db_upgrade(path, revision, selector, url)


@project.command("setup")
@click.argument("name", required=True, type=str)
@click.argument(
    "path", default=os.getcwd(), required=False, type=click.Path(exists=True)
)
def setup(name: str, path: str) -> None:
    """Creates a project directory with all needed files."""
    Manager.project_setup(name, path)


@observe.command("catalogue")
def catalogue() -> None:
    """Lists observers found in project files."""
    Manager.observe_catalogue(**Assistant.provide_context(sessions=False))


@observe.command("start")
@click.option(
    "--observer",
    help="Observer selector. Leave empty to include all observers.",
    multiple=True,
    required=False,
    type=str,
)
def start(observer: tuple[str]) -> None:
    """Starts producer/consumer ETL process."""
    context = Assistant.provide_context(_filter=observer)
    manager = Manager(**context)  # type: ignore
    manager.observe_start()


if __name__ == "__main__":
    cli(obj={})
