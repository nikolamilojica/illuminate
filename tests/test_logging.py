import sys

import click
from click.testing import CliRunner
from loguru import logger

from illuminate import __version__
from illuminate.decorators.logging import show_info
from illuminate.decorators.logging import show_logo
from illuminate.decorators.logging import show_observer_catalogue
from illuminate.manager.manager import Manager
from tests.shared.mock import Observer
from tests.shared.mock import Settings


def __get_manager(name, observers=None):
    """Manager setup function"""
    Manager._instances = {}
    manager = Manager([], name, [], "", Settings(name))
    manager.adapters = []
    manager.observers = observers or []
    manager.settings = Settings(name)
    manager.__exported = []
    manager.__failed = []
    manager.__requested = []
    manager.__requesting = []
    return manager


@click.command()
def _cli_observe_catalogue():
    """Dummy Manager command"""
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    @show_observer_catalogue
    def f(_context):
        """Dummy Assistant function"""
        return _context

    f({"observers": [Observer]})


@click.command()
def _cli_observe_start():
    """Dummy Manager command"""
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")

    @show_logo
    @show_info
    def f(_manager):
        """Dummy Manager function"""
        return _manager

    f(__get_manager("example"))


class TestLogging:
    def test_observe_catalogue(self):
        """
        Given: Manager class is instanced properly
        When: Calling function decorated with show_observer_catalogue
        Expected: Information is printed to stdout
        """
        runner = CliRunner()
        result = runner.invoke(_cli_observe_catalogue)
        assert "<class 'tests.shared.mock.Observer'>" in result.output
        assert "[('https://webscraper.io/', 'observe')]" in result.output

    def test_observe_start(self):
        """
        Given: Manager class is instanced properly
        When: Calling function decorated with show_info and show_logo
        Expected: Information is printed to stdout
        """
        runner = CliRunner()
        result = runner.invoke(_cli_observe_start)
        assert __version__ in result.output
        assert "Process started" in result.output
        assert (
            "Project files for project example loaded into context"
            in result.output
        )
        assert "Adapters discovered" in result.output
        assert "Models discovered" in result.output
        assert "Observers discovered" in result.output
        assert "Concurrency settings" in result.output
        assert "Database settings {'password': '****'}" in result.output
        assert "Observation settings" in result.output
        assert "Results gathered" in result.output
        assert "Unsuccessful observations" in result.output
        assert "Unsuccessful attempts" in result.output
        assert "Successful observations" in result.output
        assert "Number of exports" in result.output
        assert "Process finished" in result.output
