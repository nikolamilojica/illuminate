from __future__ import annotations

import asyncio
import inspect
import json
import os
from glob import glob
from pydoc import locate
from types import ModuleType
from typing import Any, Optional, Type, Union

from alembic import command
from alembic.migration import MigrationContext
from alembic.operations import Operations
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from tornado import gen, ioloop, queues

from illuminate.adapter.adapter import Adapter
from illuminate.common.project_templates import FILES
from illuminate.decorators.logging import show_info
from illuminate.decorators.logging import show_logo
from illuminate.exceptions.manager import BasicManagerException
from illuminate.exporter.exporter import Exporter
from illuminate.exporter.sql import SQLExporter
from illuminate.interface.manager import IManager
from illuminate.manager.assistant import Assistant
from illuminate.meta.singleton import Singleton
from illuminate.observation.http import HTTPObservation
from illuminate.observation.http import Observation
from illuminate.observer.finding import Finding
from illuminate.observer.observer import Observer


class Manager(IManager, metaclass=Singleton):
    """Manager class, responsible for framework cli commands"""

    def __init__(
        self,
        adapters: list[Type[Adapter]],
        name: str,
        observers: list[Type[Observer]],
        path: str,
        settings: ModuleType,
        *args,
        **kwargs,
    ):
        self.adapters = adapters
        self.name = name
        self.observers = observers
        self.path = path
        self.sessions = self._create_sessions(settings)
        self.settings = settings
        self.__observe_queue: queues.Queue = queues.Queue()
        self.__adapt_queue: queues.Queue = queues.Queue()
        self.__export_queue: queues.Queue = queues.Queue()
        self.__exported: set = set()
        self.__failed: set = set()
        self.__requested: set = set()
        self.__requesting: set = set()

    @property
    def failed(self) -> set:
        return self.__failed

    @property
    def exported(self) -> set:
        return self.__exported

    @property
    def requested(self) -> set:
        return self.__requested

    @staticmethod
    def db_populate(
        fixtures: tuple[str],
        selector: str,
        url: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        """Populates db with Alembic framework"""
        settings = Assistant.import_settings()
        if not url:
            url = Assistant.create_db_url(selector, settings)
        engine = create_engine(url)
        context = MigrationContext.configure(engine.connect())
        op = Operations(context)
        table_data = {}
        files = (
            fixtures if fixtures else glob("fixtures/*.json", recursive=True)
        )
        for file in files:
            logger.info(f"Database fixtures file discovered {file}")
        for _file in files:
            with open(_file, "r") as file:  # type: ignore
                content = json.load(file)  # type: ignore
                for table in content:
                    table_data.update({table["name"]: table["data"]})
        models = [locate(i) for i in settings.MODELS]
        for model in models:
            if model.__tablename__ in table_data:  # type: ignore
                data = table_data[model.__tablename__]  # type: ignore
                op.bulk_insert(model.__table__, data)  # type: ignore
                for record in data:
                    logger.debug(
                        f"Row {record} added to "  # type: ignore
                        f"table {model.__tablename__}"
                    )
        logger.success(f"Database {selector} populated")

    @staticmethod
    def db_revision(
        path: str,
        revision: str,
        selector: str,
        url: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
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
        logger.success("Revision created")

    @staticmethod
    def db_upgrade(
        path: str,
        revision: str,
        selector: str,
        url: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        """Performs db migration with Alembic framework"""
        settings = Assistant.import_settings()
        if not url:
            url = Assistant.create_db_url(selector, settings)
        config = Assistant.create_alembic_config(path, url)
        command.upgrade(config, revision)
        logger.success(f"Database {selector} upgraded")

    @staticmethod
    def project_setup(name: str, path: str, *args, **kwargs) -> None:
        """Create project directory and populates it with project files"""

        if path != ".":
            path = os.path.join(path, name)
            if os.path.exists(path):
                raise BasicManagerException("Directory already exists")
            logger.opt(colors=True).info(
                f"Creating project directory for project "
                f"<yellow>{name}</yellow>"
            )
            os.mkdir(path)

        for _name, content in FILES.items():
            file_path = os.path.join(path, _name)
            if os.sep in _name:
                os.makedirs(
                    os.sep.join(file_path.split(os.sep)[:-1]), exist_ok=True
                )
            with open(file_path, "w") as file:
                logger.debug(f"Creating project file {_name} at {file_path}")
                file.write(f"{content.format(name=name).strip()}\n")

        logger.success(f"Project structure created for {name}")

    @show_logo
    @show_info
    def observe_start(self) -> None:
        """Start producer/consumer ETL process based on project files"""
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self._observe_start)

    @staticmethod
    def _create_sessions(settings: ModuleType) -> dict[str, dict[str, Any]]:
        """Create sessions dictionary from settings"""
        _sessions: dict[str, dict[str, Any]] = {
            "mysql": {},
            "postgresql": {},
        }
        logger.opt(colors=True).info(
            f"Number of expected db connections: "
            f"<yellow>{len(settings.DB)}</yellow>"
        )
        for db in settings.DB:
            if settings.DB[db]["type"] in ("mysql", "postgresql"):
                url = Assistant.create_db_url(db, settings, _async=True)
                engine = create_async_engine(url)
                session = sessionmaker(
                    engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                )
                host = settings.DB[db]["host"]
                port = settings.DB[db]["port"]
                logger.opt(colors=True).info(
                    f"Adding session with <yellow>{db}</yellow> at "
                    f"<magenta>{host}:{port}</magenta> to context"
                )
                _sessions[settings.DB[db]["type"]] = {db: session}
        return _sessions

    async def __start(self) -> None:
        """Initialize observers and schedule initial observations"""
        for observer in self.observers:
            instance = observer()
            logger.opt(colors=True).info(
                f"Observer <yellow>{instance.NAME}</yellow> initialized"
            )
            for _observation in instance.initial_observations:
                await self.__observation(_observation)

    async def __router(
        self, item: Union[Exporter, Finding, Observation]
    ) -> None:
        """Route item based on its class to proper queue"""
        if isinstance(item, Exporter):
            await self.__export_queue.put(item)
        elif isinstance(item, Finding):
            if inspect.stack()[1][3] != "__adaptation":
                await self.__adapt_queue.put(item)
            else:
                logger.warning(
                    f"Findings can only yield Exporters and Observations "
                    f"thus rejecting item {item}"
                )
        elif isinstance(item, Observation):
            if isinstance(item, HTTPObservation) and item.allowed:
                await self.__observe_queue.put(item)
        else:
            logger.warning(
                f"Manager rejected item {item} due to unsupported "
                f"item type {type(item)}"
            )

    async def __observe(self) -> None:
        """Take item from observe queue and schedule observation after delay"""
        async for item in self.__observe_queue:
            if not item:
                return
            await asyncio.sleep(
                self.settings.OBSERVATION_CONFIGURATION["delay"]
            )
            await self.__observation(item)
            logger.debug(f"Coroutine observed {item}")
            del item
            self.__observe_queue.task_done()

    async def __observation(self, item: Observation) -> None:
        """Pass item based on its type to proper observation function"""
        if isinstance(item, HTTPObservation):
            await self.__observation_http(item)

    async def __observation_http(self, item: HTTPObservation) -> None:
        """Configure HTTP observation and perform observe with a callback"""
        item.configuration = {
            **self.settings.OBSERVATION_CONFIGURATION["http"],
            **item.configuration,
        }
        if item.url in self.__requesting:
            return
        self.__requesting.add(item.url)
        items = await item.observe()
        if not items:
            self.__failed.add(item.url)
            return
        self.__requested.add(item.url)
        async for _item in items:
            await self.__router(_item)

    async def __adapt(self) -> None:
        """Take item from adapt queue and schedule adaptions"""
        async for item in self.__adapt_queue:
            if not item:
                return
            await self.__adaptation(item)
            logger.debug(f"Coroutine adapted {item}")
            del item
            self.__adapt_queue.task_done()

    async def __adaptation(self, item: Finding) -> None:
        """Instance adapters and perform adapt on item"""
        for adapter in self.adapters:
            instance = adapter()

            for subscriber in instance.subscribers:
                if isinstance(item, subscriber):
                    items = instance.adapt(item)
                    async for _item in items:  # type: ignore
                        await self.__router(_item)

    async def __export(self) -> None:
        """Take item from export queue and schedule exportation"""
        async for item in self.__export_queue:
            if not item:
                return
            await self.__exportation(item)
            logger.debug(f"Coroutine exported {item}")
            del item
            self.__export_queue.task_done()

    async def __exportation(self, item: Exporter) -> None:
        """Pass item based on its type to proper exportation function"""
        if isinstance(item, SQLExporter):
            await self.__exportation_sql(item)

    async def __exportation_sql(self, item: SQLExporter) -> None:
        """Perform SQL export on item"""
        try:
            session = self.sessions[item.type][item.name]
            await item.export(session)
            self.__exported.add(item.model)
        except KeyError:
            logger.critical(
                f"Database {item.name} of a type {item.type} "
                f"is not found in context"
            )

    @logger.catch
    async def _observe_start(self) -> None:
        """Main async function"""
        self.adapters.sort(key=lambda x: x.priority, reverse=True)

        _observers = self.settings.CONCURRENCY["observers"]
        _adapters = self.settings.CONCURRENCY["adapters"]
        _exporters = self.settings.CONCURRENCY["exporters"]

        observers = gen.multi([self.__observe() for _ in range(_observers)])
        adapters = gen.multi([self.__adapt() for _ in range(_adapters)])
        exporters = gen.multi([self.__export() for _ in range(_exporters)])

        await self.__start()
        await self.__observe_queue.join()
        await self.__adapt_queue.join()
        await self.__export_queue.join()

        for _ in range(_observers):
            await self.__observe_queue.put(None)
        for _ in range(_adapters):
            await self.__adapt_queue.put(None)
        for _ in range(_exporters):
            await self.__export_queue.put(None)

        await observers
        await adapters
        await exporters
