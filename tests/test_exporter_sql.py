import os

import pytest

from illuminate.exceptions import BasicExporterException
from illuminate.exporter import SQLExporter
from illuminate.manager import Manager
from tests.shared.unit import Test


class TestExporterSQL(Test):
    @pytest.mark.asyncio
    @pytest.mark.xfail(raises=BasicExporterException)
    async def test_export_unsuccessfully(self):
        """
        Given: Current directory is a project directory
        When: Exporting model and process fails
        Expected: BasicExporterException is raised
        """
        with pytest.raises(BasicExporterException):
            with self.path() as path:
                name = "example"
                Manager.project_setup(name, ".")
                from models.example import ModelExample

                Manager.db_revision(path, "head", "main", self.url)
                Manager.db_upgrade(path, "head", "main", self.url)
                title = "Example"
                url = "https//:example.com"
                model = ModelExample(title=title, url=url)
                exporter = SQLExporter(model=model)
                os.remove(os.path.join(path, f"{self.db}.db"))
                await exporter.export(self.session_async)

    @pytest.mark.asyncio
    async def test_export_successfully(self):
        """
        Given: Current directory is a project directory
        When: Exporting/committing a model
        Expected: Data is placed in database
        """
        with self.path() as path:
            name = "example"
            Manager.project_setup(name, ".")
            from models.example import ModelExample

            Manager.db_revision(path, "head", "main", self.url)
            Manager.db_upgrade(path, "head", "main", self.url)
            title = "Example"
            url = "https//:example.com"
            model = ModelExample(title=title, url=url)
            exporter = SQLExporter(model=model)
            await exporter.export(self.session_async)
            query = self.session.query(ModelExample).all()
            assert query[0].title == title
            assert query[0].url == url
