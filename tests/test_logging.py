import sys

import click
from click.testing import CliRunner
from loguru import logger

from illuminate import __version__
from illuminate.decorators.logging import show_info
from illuminate.decorators.logging import show_logo
from illuminate.manager.manager import Manager


@click.command()
def _cli():
    """Dummy Manager command"""
    logger.remove()
    logger.add(sys.stdout, level="DEBUG")

    class Settings:
        """Dummy Manager settings"""

        def __init__(self, name):
            self.CONCURRENCY = {}
            self.DB = {}
            self.MODELS = []
            self.NAME = name
            self.OBSERVER_CONFIGURATION = {}

    @show_logo
    @show_info
    def f(_manager):
        """Dummy Manager function"""
        return _manager

    manager = Manager(name="example")
    manager.adapters = []
    manager.observers = []
    manager.settings = Settings("example")
    manager.__exported = []
    manager.__failed = []
    manager.__requested = []
    manager.__requesting = []
    f(manager)


class TestLogging:
    def test_logging(self):
        """
        Given: Manager class is instanced properly
        When: Calling function decorated with show_info and show_logo
        Expected: Information is printed to stdout
        """
        runner = CliRunner()
        result = runner.invoke(_cli)
        assert __version__ in result.output
        assert "Process started" in result.output
        assert "Project files for project example loaded into context" in result.output
        assert "Adapters discovered" in result.output
        assert "Models discovered" in result.output
        assert "Observers discovered" in result.output
        assert "Concurrency settings" in result.output
        assert "Database settings {'password': '****'}" in result.output
        assert "Observer settings" in result.output
        assert "Results gathered" in result.output
        assert "Unsuccessful observations" in result.output
        assert "Unsuccessful attempts" in result.output
        assert "Successful observations" in result.output
        assert "Number of exports" in result.output
        assert "Process finished" in result.output
