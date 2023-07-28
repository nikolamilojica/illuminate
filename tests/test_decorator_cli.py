import pytest
from alembic.config import Config
from alembic.operations import Operations

from illuminate.decorators import adapt
from illuminate.exceptions import BasicManagerException
from illuminate.manager import Manager
from tests.unit import Test


class DummyManager:
    """Dummy Manager class."""

    @staticmethod
    @adapt
    def db_populate(fixtures, models, operations, selector):
        """Dummy db_populate."""
        assert len(models) == 1
        assert len(fixtures) == 1
        assert isinstance(operations, Operations)
        assert selector == "main"

    @staticmethod
    @adapt
    def db_revision(config, revision):
        """Dummy db_revision."""
        assert isinstance(config, Config)
        assert revision == "head"

    @staticmethod
    @adapt
    def db_upgrade(config, revision, selector):
        """Dummy db_upgrade."""
        assert isinstance(config, Config)
        assert revision == "head"
        assert selector == "main"


class TestAdapt(Test):
    def test_db_populate(self):
        """
        Given: Current directory is a project directory
        When: Calling Manager.db_revision with cli arguments
        Expected: Manager.db_populate is adapted
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
        Expected: Manager.db_revision is adapted
        """
        with self.path() as path:
            Manager.project_setup("example", ".")
            DummyManager.db_revision(path, "head", "main", self.url)

    def test_db_upgrade(self):
        """
        Given: Current directory is a project directory
        When: Calling Manager.db_revision with cli arguments
        Expected: Manager.db_upgrade is adapted
        """
        with self.path() as path:
            Manager.project_setup("example", ".")
            DummyManager.db_upgrade(path, "head", "main", self.url)


class TestAdaptExceptions(Test):

    influxdb_url = "influxdb://son:son@localhost/example"

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_db_populate_type_exception(self):
        """
        Given: Current directory is a project directory, revision file is
        created and upgrade is executed
        When: Populating database referencing wrong database type
        Expected: BasicManagerException is raised
        """
        with pytest.raises(BasicManagerException):
            with self.path() as path:
                Manager.project_setup("example", ".")
                Manager.db_revision(path, "head", "main", self.url)
                Manager.db_upgrade(path, "head", "main", self.url)
                Manager.db_populate(
                    ("fixtures/example.json",),
                    "measurements",
                    self.influxdb_url,
                )

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_db_revision_type_exception(self):
        """
        Given: Current directory is a project directory
        When: Creating revision file referencing wrong database type
        Expected: BasicManagerException is raised
        """
        with pytest.raises(BasicManagerException):
            with self.path() as path:
                Manager.project_setup("example", ".")
                Manager.db_revision(
                    path, "head", "measurements", self.influxdb_url
                )

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_db_upgrade_type_exception(self):
        """
        Given: Current directory is a project directory and revision file is
        created
        When: Upgrading database referencing wrong database type
        Expected: BasicManagerException is raised
        """
        with pytest.raises(BasicManagerException):
            with self.path() as path:
                Manager.project_setup("example", ".")
                Manager.db_revision(path, "head", "main", self.url)
                Manager.db_upgrade(
                    path, "head", "measurements", self.influxdb_url
                )
