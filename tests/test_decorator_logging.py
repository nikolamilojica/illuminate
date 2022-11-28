import sys

import click
from click.testing import CliRunner
from loguru import logger

from illuminate import __version__
from illuminate.decorators.logging import show_info
from illuminate.decorators.logging import show_logo
from illuminate.decorators.logging import show_observer_catalogue
from illuminate.manager.assistant import Assistant
from illuminate.manager.manager import Manager
from tests.shared.unit import Test


def __get_context(name):
    """Context fetch function."""
    test = Test()
    with test.path():
        Manager.project_setup(name, ".")
        context = Assistant.provide_context()
    return context


def __get_manager(name):
    """Manager setup function."""
    test = Test()
    with test.path():
        Manager.project_setup(name, ".")
        context = Assistant.provide_context()
        manager = Manager(**context)
    return manager


@click.command()
def _cli_observe_catalogue():
    """Dummy Manager command."""
    logger.remove()
    logger.add(sys.stdout, level="INFO")

    @show_observer_catalogue
    def f(_context):
        """Dummy Assistant function."""
        return _context

    f(__get_context("example"))


@click.command()
def _cli_observe_start():
    """Dummy Manager command."""
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")

    @show_logo
    @show_info
    def f(_manager):
        """Dummy Manager function."""
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
        assert (
            "<class 'observers.example.py.ObserverExample'>" in result.output
        )
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
        assert "Observation settings" in result.output
        assert "Results gathered" in result.output
        assert "Unsuccessful observations" in result.output
        assert "Unsuccessful attempts" in result.output
        assert "Successful observations" in result.output
        assert "Number of exports" in result.output
        assert "Process finished" in result.output
