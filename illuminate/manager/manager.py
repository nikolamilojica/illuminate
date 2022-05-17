import json
import os
from glob import glob
from pydoc import locate

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine

from illuminate.common.project_templates import FILES
from illuminate.discrete.manager.interface import Interface
from illuminate.exceptions.manager import BasicManagerException
from illuminate.meta.singleton import Singleton


class Manager(Interface, metaclass=Singleton):
    @staticmethod
    def create_alembic_config(path, url):
        """Creates config object needed to perform Alembic commands"""
        config = Config()
        config.set_main_option("script_location", os.path.join(path, "migrations"))
        config.set_main_option("sqlalchemy.url", url)
        return config

    @staticmethod
    def db_url_from_settings(selector, settings):
        """Creates db url from data in settings.py module"""
        db = settings.DB[selector]
        db["db"] = settings.NAME
        return "{type}://{user}:{pass}@{host}/{db}".format(**db)

    @staticmethod
    def obtain_project_settings():
        """Tries to import project settings.py module and returns it"""
        try:
            import settings
            return settings
        except ImportError:
            raise BasicManagerException

    def __init__(self, name=None, path=None, *args, **kwargs):
        self.name = name
        self.path = path

    @staticmethod
    def db_populate(fixtures, selector, url=None, *args, **kwargs):
        """Populates db with Alembic framework"""
        settings = Manager.obtain_project_settings()
        if not url:
            url = Manager.db_url_from_settings(selector, settings)
        engine = create_engine(url)
        context = MigrationContext.configure(engine.connect())
        op = Operations(context)
        table_data = {}
        files = fixtures if fixtures else glob('fixtures/*.json', recursive=True)
        for _file in files:
            with open(_file, 'r') as file:
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
        settings = Manager.obtain_project_settings()
        if not url:
            url = Manager.db_url_from_settings(selector, settings)
        config = Manager.create_alembic_config(path, url)
        command.revision(
            config,
            message=settings.NAME,
            autogenerate=True,
            head=revision,
        )

    @staticmethod
    def db_upgrade(path, revision, selector, url=None, *args, **kwargs):
        """Performs db migration with Alembic framework"""
        settings = Manager.obtain_project_settings()
        if not url:
            url = Manager.db_url_from_settings(selector, settings)
        config = Manager.create_alembic_config(path, url)
        command.upgrade(config, revision)

    @staticmethod
    def setup(name, path, *args, **kwargs):
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
