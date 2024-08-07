import asyncio
import io
import math
import os
from os import walk

import pytest
from sqlalchemy import inspect
from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPResponse

from illuminate.common import FILES
from illuminate.exceptions import BasicManagerException
from illuminate.manager import Assistant
from illuminate.manager import Manager
from tests.unit import Test


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
    def test_db_populate_unsuccessfully(self):
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
        Expected: File migrations/versions/<REV_ID>.py exists
        """
        with self.path() as path:
            name = "example"
            Manager.project_setup(name, ".")
            Manager.db_revision(path, "head", "main", self.url)
            versions = os.path.join(path, "migrations/versions/")
            assert os.path.isdir(versions)
            for file in next(walk(versions), (None, None, []))[2]:
                if file.endswith(".py"):
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
            load_time = 1.0
            query = self.session.query(ModelExample).all()
            assert len(query) == 2
            assert math.isclose(
                query[0].load_time,
                load_time,
                rel_tol=1e-09,
                abs_tol=1e-09,
            )
            assert math.isclose(
                query[0].load_time,
                load_time,
                rel_tol=1e-09,
                abs_tol=1e-09,
            )
            assert query[0].url == "https://webscraper.io/"
            assert query[1].url == "https://webscraper.io/tutorials"
            assert (
                query[0].title == "Web Scraper - The #1 web scraping extension"
            )
            assert query[1].title == "Web Scraper Tutorials"


class TestManagerProjectCommandGroup(Test):
    @pytest.mark.xfail(raises=BasicManagerException)
    def test_project_setup_unsuccessfully(self):
        """
        Given: Directory of file exists with the same name as project
        When: Setting up new project
        Expected: Raise exception
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


class TestManagerObserveCommandGroup(Test):

    function = "tornado.httpclient.AsyncHTTPClient.fetch"

    @staticmethod
    @pytest.fixture(scope="function")
    def async_http_responses_ok(mocker):
        """
        Patch fetch function to return predefined response object.
        """
        body = b"""
        <!DOCTYPE HTML>
        <html lang="en">
        <head>
        <META charset="UTF-8">
        <META name="viewport"
         content="width=device-width, initial-scale=1.0">
        <title>Example</title>
        </head>
        <body>
        <p>
        Example
        </p>
        </body>
        </html>
        """
        future = asyncio.Future()
        request = HTTPRequest("https://example.com")
        response = HTTPResponse(request, 200, None, io.BytesIO(body))
        future.set_result(response)
        mocker.patch(
            TestManagerObserveCommandGroup.function, return_value=future
        )

    def test_observe_start_successfully(self, async_http_responses_ok):
        """
        Given: Current working directory is already configured project
        When: Observation process is done
        Expected: Data is exported to database
        """
        with self.path() as path:
            name = "example"
            Manager.project_setup(name, ".")
            from models.example import ModelExample

            Manager.db_revision(path, "head", "main", self.url)
            Manager.db_upgrade(path, "head", "main", self.url)
            context = Assistant.provide_context()
            manager = Manager(**context)
            manager.sessions["main"] = self.session_async
            manager.observe_start()

            query = self.session.query(ModelExample).all()
            assert len(manager.exported) == 1
            assert len(manager.observed) == 1
            assert len(query) == 1
            assert query[0].url == "https://example.com"
            assert query[0].title == "Example"
