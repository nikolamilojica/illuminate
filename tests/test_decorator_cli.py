from alembic.config import Config
from alembic.operations import Operations

from illuminate.decorators.cli import overload
from illuminate.manager.manager import Manager
from tests.shared.unit import Test


class DummyManager:
    """Dummy Manager class"""

    @staticmethod
    @overload
    def db_populate(fixtures, models, operations, selector):
        """Dummy db_populate"""
        assert len(models) == 1
        assert len(fixtures) == 1
        assert isinstance(operations, Operations)
        assert selector == "main"

    @staticmethod
    @overload
    def db_revision(config, revision):
        """Dummy db_revision"""
        assert isinstance(config, Config)
        assert revision == "head"

    @staticmethod
    @overload
    def db_upgrade(config, revision, selector):
        """Dummy db_upgrade"""
        assert isinstance(config, Config)
        assert revision == "head"
        assert selector == "main"


class TestOverload(Test):
    def test_db_populate(self):
        """
        Given: Current directory is a project directory
        When: Calling Manager.db_revision with cli arguments
        Expected: Manager.db_populate is overridden
        """
        with self.path():
            Manager.project_setup("example", ".")
            DummyManager.db_populate(
                ("fixtures/example.json",), "main", self.url
            )

    def test_db_revision(self):
        """
        Given: Current directory is a project directory
        When: Calling Manager.db_revision with cli arguments
        Expected: Manager.db_revision is overridden
        """
        with self.path() as path:
            Manager.project_setup("example", ".")
            DummyManager.db_revision(path, "head", "main", self.url)

    def test_db_upgrade(self):
        """
        Given: Current directory is a project directory
        When: Calling Manager.db_revision with cli arguments
        Expected: Manager.db_upgrade is overridden
        """
        with self.path() as path:
            Manager.project_setup("example", ".")
            DummyManager.db_upgrade(path, "head", "main", self.url)
