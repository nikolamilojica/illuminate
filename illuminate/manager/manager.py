import json
import os
from glob import glob
from pydoc import locate

from alembic import command
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine

from illuminate.common.project_templates import FILES
from illuminate.discrete.manager.manager import Interface
from illuminate.exceptions.manager import BasicManagerException
from illuminate.manager.assistant import Assistant
from illuminate.meta.singleton import Singleton


class Manager(Interface, metaclass=Singleton):
    def __init__(self, name=None, path=None, *args, **kwargs):
        self.name = name
        self.path = path

    @staticmethod
    def db_populate(fixtures, selector, url=None, *args, **kwargs):
        """Populates db with Alembic framework"""
        settings = Assistant.import_settings()
        if not url:
            url = Assistant.create_db_url(selector, settings)
        engine = create_engine(url)
        context = MigrationContext.configure(engine.connect())
        op = Operations(context)
        table_data = {}
        files = fixtures if fixtures else glob("fixtures/*.json", recursive=True)
        for _file in files:
            with open(_file, "r") as file:
                content = json.load(file)
                for table in content:
                    table_data.update({table["name"]: table["data"]})
        models = [locate(i) for i in settings.MODELS]
        for model in models:
            if model.__tablename__ in table_data:
                # TODO: log insert process
                op.bulk_insert(model.__table__, table_data[model.__tablename__])

    @staticmethod
    def db_revision(path, revision, selector, url=None, *args, **kwargs):
        """Creates db revision with Alembic framework"""
        settings = Assistant.import_settings()
        if not url:
            url = Assistant.create_db_url(selector, settings)
        config = Assistant.create_alembic_config(path, url)
        command.revision(
            config,
            message=settings.NAME,
            autogenerate=True,
            head=revision,
        )

    @staticmethod
    def db_upgrade(path, revision, selector, url=None, *args, **kwargs):
        """Performs db migration with Alembic framework"""
        settings = Assistant.import_settings()
        if not url:
            url = Assistant.create_db_url(selector, settings)
        config = Assistant.create_alembic_config(path, url)
        command.upgrade(config, revision)

    @staticmethod
    def project_setup(name, path, *args, **kwargs):
        """Create project directory and populates it with project files"""

        if path != ".":
            path = os.path.join(path, name)
            if os.path.exists(path):
                raise BasicManagerException
            os.mkdir(path)

        for _name, content in FILES.items():
            file_path = os.path.join(path, _name)
            if os.sep in _name:
                os.makedirs(os.sep.join(file_path.split(os.sep)[:-1]), exist_ok=True)
            with open(file_path, "w") as file:
                file.write(f"{content.format(name=name).strip()}\n")
