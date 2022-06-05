import json
import os
from datetime import timedelta
from glob import glob
from pydoc import locate

from alembic import command
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine
from tornado import gen, ioloop, queues

from illuminate.common.project_templates import FILES
from illuminate.discrete.manager.manager import Interface
from illuminate.exceptions.manager import BasicManagerException
from illuminate.extraction.http import HTTPExtraction
from illuminate.manager.assistant import Assistant
from illuminate.meta.singleton import Singleton
from illuminate.observer.observation import Observation


class Manager(Interface, metaclass=Singleton):
    def __init__(
        self,
        exporters=None,
        name=None,
        observers=None,
        path=None,
        settings=None,
        *args,
        **kwargs,
    ):
        self.exporters = exporters
        self.name = name
        self.observers = observers
        self.path = path
        self.settings = settings
        self.__extract_queue = queues.Queue()
        self.__transform_queue = queues.Queue()
        self.__load_queue = queues.Queue()
        self.__failed = set()
        self.__requested = set()
        self.__requesting = set()

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

    def observe_start(self):
        """Start producer/consumer ETL process based on project files"""
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self._observe_start)

    async def _observe_start(self):
        """Main async function"""
        eq = self.__extract_queue
        tq = self.__transform_queue
        lq = self.__load_queue
        failed = self.__failed
        requested = self.__requested
        requesting = self.__requesting
        settings = self.settings

        async def execute(observers):
            for observer in observers:
                instance = observer()
                for observation in instance.initial_observations:
                    await extract(observation)

        async def extractor():
            async for item in eq:
                if not item:
                    return
                await extract(item)
                eq.task_done()

        async def extract(item):
            items = None
            if isinstance(item, HTTPExtraction):
                if item.url in requesting:
                    return
                requesting.add(item.url)
                items = await item.callback()
                if not items:
                    failed.add(item.url)
                    return
                requested.add(item.url)
            async for item in items:
                await extraction_router(item)

        async def extraction_router(item):
            if isinstance(item, Observation):
                await tq.put(item)
            if isinstance(item, HTTPExtraction):
                if item.allowed:
                    await eq.put(item)

        async def loader():
            async for item in lq:
                if not item:
                    return
                await load(item)
                lq.task_done()

        async def load(item):
            """End of line"""

        async def transformer():
            async for item in tq:
                if not item:
                    return
                await transform(item)
                tq.task_done()

        async def transform(item):
            await lq.put(item)

        con = settings.CONCURRENCY
        extractors = gen.multi([extractor() for _ in range(con)])
        transformers = gen.multi([transformer() for _ in range(con)])
        loaders = gen.multi([loader() for _ in range(con)])

        await execute(self.observers)
        await eq.join(timeout=timedelta(seconds=300))
        await tq.join(timeout=timedelta(seconds=300))
        await lq.join(timeout=timedelta(seconds=300))

        for _ in range(settings.CONCURRENCY):
            await eq.put(None)
            await tq.put(None)
            await lq.put(None)

        await extractors
        await transformers
        await loaders
