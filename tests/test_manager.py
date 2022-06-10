import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from os import walk

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from illuminate.common.project_templates import FILES
from illuminate.exceptions.manager import BasicManagerException
from illuminate.manager.manager import Manager


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


class TestManagerDBCommandGroup:
    RUNTIME_PERSISTENT_FOLDER = "/tmp/example"
    RUNTIME_PERSISTENT_DB_URL = f"sqlite:///{RUNTIME_PERSISTENT_FOLDER}/example.db"

    @classmethod
    def setup_class(cls):
        """
        Test class setup method
        :return: None
        """
        os.mkdir(cls.RUNTIME_PERSISTENT_FOLDER)

    @classmethod
    def teardown_class(cls):
        """
        Test class teardown method
        :return: None
        """
        shutil.rmtree(cls.RUNTIME_PERSISTENT_FOLDER)

    @contextmanager
    def force_python_path(self, path):
        """
        Put directory path to PYTHONPATH temporarily and use it as cwd
        :param path: directory path: str
        :yields: _GeneratorContextManager
        """
        sys.path.append(path)
        os.chdir(path)
        yield
        sys.path.remove(path)

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_revision_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Creating revision of a db with Alembic
        Expected: Exception is raised
        """
        with pytest.raises(BasicManagerException) as error:
            with tempfile.TemporaryDirectory() as path:
                with self.force_python_path(path):
                    Manager.db_revision(path, "head", "main", "sqlite://")

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_upgrade_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Running db upgrade with Alembic
        Expected: Exception is raised
        """
        with pytest.raises(BasicManagerException) as error:
            with tempfile.TemporaryDirectory() as path:
                with self.force_python_path(path):
                    Manager.db_upgrade(path, "head", "main", "sqlite://")

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_populate_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Running db populate
        Expected: Exception is raised
        """
        with pytest.raises(BasicManagerException) as error:
            with tempfile.TemporaryDirectory() as path:
                with self.force_python_path(path):
                    Manager.db_upgrade(path, "head", "main", "sqlite://")

    def test_revision_successfully(self):
        """
        Given: Current directory is a project directory
        When: Creating revision of a db with Alembic
        Expected: File migrations/versions/<REV_ID>_<PROJECT_NAME>.py exists
        """
        path = self.RUNTIME_PERSISTENT_FOLDER
        with self.force_python_path(path):
            name = "example"
            Manager.project_setup(name, ".")
            Manager.db_revision(path, "head", "main", "sqlite://")
        versions = os.path.join(path, "migrations/versions/")
        assert os.path.isdir(versions)
        for file in next(walk(versions), (None, None, []))[2]:
            if name in file:
                assert True
                return
        assert False

    def test_upgrade_successfully(self):
        """
        Given: Current directory is a project directory
        When: Running db upgrade with Alembic
        Expected: Modify db schema to match model definitions
        """
        path = self.RUNTIME_PERSISTENT_FOLDER
        url = self.RUNTIME_PERSISTENT_DB_URL
        engine = create_engine(url)
        with self.force_python_path(path):
            Manager.db_upgrade(path, "head", "main", url)
        data = inspect(engine)
        assert "example" in data.get_table_names()

    def test_populate_successfully(self):
        """
        Given: Current directory is a project directory
        When: Running db populate
        Expected: Populate db with data in fixture files
        """
        path = self.RUNTIME_PERSISTENT_FOLDER
        url = self.RUNTIME_PERSISTENT_DB_URL
        engine = create_engine(url)
        with self.force_python_path(path):
            from models.example import ModelExample

            Manager.db_populate(["fixtures/example.json"], "main", url)
        session = sessionmaker(engine)()
        session.query(ModelExample).all()
        query = session.query(ModelExample).all()
        assert len(query) == 2
        assert query[0].url == "https://example.mock/category/product/1"
        assert query[1].url == "https://example.mock/category/product/2"
        assert query[0].title == "Product 1"
        assert query[1].title == "Product 2"


class TestManagerProjectCommandGroup:
    @staticmethod
    def assert_project_structure(name, path, cwd=False):
        """
        Helper method for asserting project structure
        :param name: name of the project: str
        :param path: path of the project: str
        :param cwd: assert in same folder: bool
        :return: None
        """
        project_path = os.path.join(path, name) if not cwd else path
        assert os.path.exists(project_path)
        for _name, content in FILES.items():
            test_file_path = os.path.join(project_path, _name)
            assert os.path.exists(test_file_path)
            with open(test_file_path, "r") as file:
                assert content.format(name=name).strip() == file.read().strip()

    def test_setup_successfully(self):
        """
        Given: No directory or file exists with the same name as project
        When: Setting up new project
        Expected: Creates directories and files needed for framework
        """
        with tempfile.TemporaryDirectory() as path:
            name = "example"
            Manager.project_setup(name, path)
            self.assert_project_structure(name, path)

    def test_setup_in_current_folder_successfully(self):
        """
        Given: Current working directory is target for project files
        When: Setting up new project
        Expected: Creates directories and files needed for framework
        """
        with tempfile.TemporaryDirectory() as path:
            os.chdir(path)
            name = "example"
            Manager.project_setup(name, ".")
            self.assert_project_structure(name, path, cwd=True)

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_setup_unsuccessfully_directory_or_file_exists(self):
        """
        Given: Directory of file exists with the same name as project
        When: Setting up new project
        Expected: Raise exception
        NOTE: This test will clean files from test_setup_successfully
        """
        with pytest.raises(BasicManagerException) as error:
            name = "example"
            with tempfile.TemporaryDirectory() as path:
                Manager.project_setup(name, path)
                Manager.project_setup(name, path)
