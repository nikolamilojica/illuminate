import json
import os
from glob import glob
from pydoc import locate

from alembic import command
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tornado import gen, ioloop, queues

from illuminate.common.project_templates import FILES
from illuminate.discrete.manager.manager import Interface
from illuminate.exceptions.manager import BasicManagerException
from illuminate.manager.assistant import Assistant
from illuminate.meta.singleton import Singleton
from illuminate.observation.http import HTTPObservation
from illuminate.observer.finding import Finding


class Manager(Interface, metaclass=Singleton):
    """Manager class, responsible for framework cli commands"""

    def __init__(
        self,
        adapters=None,
        name=None,
        observers=None,
        path=None,
        settings=None,
        *args,
        **kwargs,
    ):
        self.adapters = adapters
        self.name = name
        self.observers = observers
        self.path = path
        self.sessions = None
        self.settings = settings
        self.__observe_queue = queues.Queue()
        self.__adapt_queue = queues.Queue()
        self.__export_queue = queues.Queue()
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
        _adapters = self.adapters
        _observers = self.observers
        oq = self.__observe_queue
        aq = self.__adapt_queue
        eq = self.__export_queue
        failed = self.__failed
        requested = self.__requested
        requesting = self.__requesting
        settings = self.settings

        async def start(_observers):
            for observer in _observers:
                instance = observer()
                for _observation in instance.initial_observations:
                    await observation(_observation)

        async def observe():
            async for item in oq:
                if not item:
                    return
                await observation(item)
                del item
                oq.task_done()

        async def observation(item):
            items = []
            if isinstance(item, HTTPObservation):
                if item.url in requesting:
                    return
                requesting.add(item.url)
                items = await item.observe()
                if not items:
                    failed.add(item.url)
                    return
                requested.add(item.url)
            async for _item in items:
                await observation_router(_item)

        async def observation_router(item):
            if isinstance(item, Finding):
                await aq.put(item)
            if isinstance(item, HTTPObservation):
                if item.allowed:
                    await oq.put(item)

        async def adapt():
            async for item in aq:
                if not item:
                    return
                await adaptation(item)
                del item
                aq.task_done()

        async def adaptation(item):
            for adapter in _adapters:
                instance = adapter()
                adapted = instance.adapt(item)
                async for _adaptation in adapted:
                    await eq.put(_adaptation)

        async def export(_sessions):
            async for item in eq:
                if not item:
                    return
                await exportation(item, _sessions)
                del item
                eq.task_done()

        async def exportation(item, _sessions):
            try:
                session = _sessions[item.type][item.name]
            except KeyError:
                raise BasicManagerException
            item.export(session)

        def _create_sessions():
            _sessions = {
                "mysql": {},
                "postgresql": {},
            }
            for db in settings.DB:
                if settings.DB[db]["type"] in ("mysql", "postgresql"):
                    url = Assistant.create_db_url(db, settings)
                    engine = create_engine(url)
                    session = sessionmaker(bind=engine)()
                    _sessions[settings.DB[db]["type"]] = {db: session}
            return _sessions

        self.sessions = _create_sessions()

        con = settings.CONCURRENCY
        observers = gen.multi([observe() for _ in range(con["observers"])])
        adapters = gen.multi([adapt() for _ in range(con["adapters"])])
        exporters = gen.multi([export(self.sessions) for _ in range(con["exporters"])])

        await start(_observers)
        await oq.join()
        await aq.join()
        await eq.join()

        for _ in range(con["observers"]):
            await oq.put(None)
        for _ in range(con["adapters"]):
            await aq.put(None)
        for _ in range(con["exporters"]):
            await eq.put(None)

        await observers
        await adapters
        await exporters
