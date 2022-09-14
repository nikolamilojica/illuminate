import os
from os import walk

import pytest
from sqlalchemy import inspect

from illuminate.common.project_templates import FILES
from illuminate.exceptions.manager import BasicManagerException
from illuminate.manager.manager import Manager
from tests.shared.unit import Test


class TestManagerClassInstance:
    def test_singleton_behaviour_successfully(self):
        """
        Given: None
        When: Creating instance of Manager class twice with different arguments
        Expected: Instances are the same
        """
        manager_1 = Manager("example1", "/opt/example1")
        manager_2 = Manager("example2", "/opt/example2")
        assert manager_1 == manager_2


class TestManagerDBCommandGroup(Test):
    @pytest.mark.xfail(raises=BasicManagerException)
    def test_db_revision_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Creating revision of a db with Alembic
        Expected: Exception is raised
        """
        with pytest.raises(BasicManagerException):
            with self.path() as path:
                Manager.db_revision(path, "head", "main", "")

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_db_upgrade_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Running db upgrade with Alembic
        Expected: Exception is raised
        """
        with pytest.raises(BasicManagerException):
            with self.path() as path:
                Manager.db_upgrade(path, "head", "main", "")

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_db_upgrade_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Running db populate
        Expected: Exception is raised
        """
        with pytest.raises(BasicManagerException):
            with self.path() as path:
                Manager.db_upgrade(path, "head", "main", "")

    def test_db_revision_successfully(self):
        """
        Given: Current directory is a project directory
        When: Creating revision of a db with Alembic
        Expected: File migrations/versions/<REV_ID>_<PROJECT_NAME>.py exists
        """
        with self.path() as path:
            name = "example"
            Manager.project_setup(name, ".")
            Manager.db_revision(path, "head", "main", self.url)
            versions = os.path.join(path, "migrations/versions/")
            assert os.path.isdir(versions)
            for file in next(walk(versions), (None, None, []))[2]:
                if name in file:
                    assert True
                    return
            assert False

    def test_db_upgrade_successfully(self):
        """
        Given: Current directory is a project directory
        When: Running db upgrade with Alembic
        Expected: Modify db schema to match model definitions
        """
        with self.path() as path:
            name = "example"
            Manager.project_setup(name, ".")
            Manager.db_revision(path, "head", "main", self.url)
            Manager.db_upgrade(path, "head", "main", self.url)
            data = inspect(self.engine)
            assert name in data.get_table_names()

    def test_db_populate_successfully(self):
        """
        Given: Current directory is a project directory
        When: Running db populate
        Expected: Populate db with data in fixture files
        """
        with self.path() as path:
            name = "example"
            Manager.project_setup(name, ".")
            from models.example import ModelExample

            Manager.db_revision(path, "head", "main", self.url)
            Manager.db_upgrade(path, "head", "main", self.url)
            Manager.db_populate(["fixtures/example.json"], "main", self.url)
            query = self.session.query(ModelExample).all()
            assert len(query) == 2
            assert query[0].url == "https://webscraper.io/"
            assert query[1].url == "https://webscraper.io/tutorials"
            assert query[0].title == "Web Scraper - The #1 web scraping extension"
            assert query[1].title == "Web Scraper Tutorials"


class TestManagerProjectCommandGroup(Test):
    @pytest.mark.xfail(raises=BasicManagerException)
    def test_project_setup_unsuccessfully(self):
        """
        Given: Directory of file exists with the same name as project
        When: Setting up new project
        Expected: Raise exception
        NOTE: This test will clean files from test_setup_successfully
        """
        with pytest.raises(BasicManagerException):
            with self.path() as path:
                name = "example"
                Manager.project_setup(name, path)
                Manager.project_setup(name, path)

    def test_project_setup_successfully(self):
        """
        Given: No directory or file exists with the same name as project
        When: Setting up new project
        Expected: Creates directories and files needed for framework
        """
        with self.path() as path:
            name = "example"
            Manager.project_setup(name, path)
            self.assert_project_structure(name, FILES, path)

    def test_project_setup_in_current_folder_successfully(self):
        """
        Given: Current working directory is target for project files
        When: Setting up new project
        Expected: Creates directories and files needed for framework
        """
        with self.path() as path:
            name = "example"
            Manager.project_setup(name, ".")
            self.assert_project_structure(name, FILES, path, cwd=True)
