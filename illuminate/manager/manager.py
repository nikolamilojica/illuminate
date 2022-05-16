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
    def __init__(self, name=None, path=None, *args, **kwargs):
        self.name = name
        self.path = path

    @classmethod
    def db(cls, action, path, revision, selector, url=None, *args, **kwargs):
        """Creates/changes db schema with Alembic framework"""

        try:
            import settings
        except ImportError:
            raise BasicManagerException

        db = settings.DB[selector]
        db["db"] = settings.NAME
        if not url:
            # TODO: URL from settings
            url = "{type}://{user}:{pass}@{host}/{db}".format(**db)
        migrations = os.path.join(path, "migrations")

        config = Config()
        config.set_main_option("script_location", migrations)
        config.set_main_option("sqlalchemy.url", url)
        #  TODO: logging, try/except with Alembic/SQLAlchemy exceptions

        if action == "populate":
            #  TODO: consider using function/method
            eng = create_engine(url)
            ctx = MigrationContext.configure(eng.connect())
            ops = Operations(ctx)
            table_data = {}
            for _file in glob('fixtures/*.json', recursive=True):
                with open(_file, 'r') as file:
                    content = json.load(file)
                    for table in content:
                        table_data.update({table["name"]: table["data"]})
            models = [locate(i) for i in settings.MODELS]
            for model in models:
                if model.__tablename__ in table_data:
                    ops.bulk_insert(model.__table__, table_data[model.__tablename__])
        elif action == "revision":
            command.revision(
                config,
                message=settings.NAME,
                autogenerate=True,
                head=revision,
            )
        elif action == "upgrade":
            command.upgrade(config, revision)
        else:
            raise BasicManagerException

    @classmethod
    def setup(cls, name, path, *args, **kwargs):
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
