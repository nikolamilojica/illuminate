from __future__ import annotations

import asyncio
import inspect
import json
import os
import traceback
from glob import glob
from types import ModuleType
from typing import Type, Union

from aioinflux import InfluxDBClient  # type: ignore
from alembic import command
from alembic.config import Config
from alembic.operations import Operations
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from tornado import gen, ioloop, queues

from illuminate.adapter import Adapter
from illuminate.common import FILES
from illuminate.decorators import adapt
from illuminate.decorators import show_info
from illuminate.decorators import show_logo
from illuminate.decorators import show_observer_catalogue
from illuminate.exceptions import BasicExporterException
from illuminate.exceptions import BasicManagerException
from illuminate.exporter import Exporter
from illuminate.exporter import InfluxDBExporter
from illuminate.exporter import SQLExporter
from illuminate.interface import IManager
from illuminate.meta.type import Result
from illuminate.observation import FileObservation
from illuminate.observation import HTTPObservation
from illuminate.observation import Observation
from illuminate.observation import SQLObservation
from illuminate.observation import SplashObservation
from illuminate.observer import Finding
from illuminate.observer import Observer


class Manager(IManager):
    """
    Manager class, executes framework's cli commands.

    All public methods correspond to cli commands. It should only be
    instantiated when 'illuminate observe start' command is used with kwargs
    provided by Assistant class.
    """

    def __init__(
        self,
        adapters: list[Type[Adapter]],
        name: str,
        observers: list[Type[Observer]],
        path: str,
        sessions: dict[str, Union[Type[AsyncSession], InfluxDBClient]],
        settings: ModuleType,
        *args,
        **kwargs,
    ):
        """
        Manager's __init__ method.

        :param adapters: List of Adapters found in project files
        :param name: Project's name
        :param observers: List of Observers found in project files after
        filtering
        :param path: Path to project files
        :param sessions: Database sessions
        :param settings: Project's settings.py module
        """
        self.adapters = adapters
        self.name = name
        self.observers = observers
        self.path = path
        self.sessions = sessions
        self.settings = settings
        self._adapters: list[Adapter] = []
        self._observers: list[Observer] = []
        self.__observe_queue: queues.Queue = queues.Queue()
        self.__adapt_queue: queues.Queue = queues.Queue()
        self.__export_queue: queues.Queue = queues.Queue()
        self.__exported: set = set()
        self.__not_observed: set = set()
        self.__observed: set = set()
        self.__observing: set = set()

    @property
    def exported(self) -> set:
        return self.__exported

    @property
    def not_observed(self) -> set:
        return self.__not_observed

    @property
    def observed(self) -> set:
        return self.__observed

    @staticmethod
    @adapt
    def db_populate(
        fixtures: tuple[str],
        models: list[object],
        operations: Operations,
        selector: str,
    ) -> None:
        """
        Populates database with fixtures.

        :param fixtures: Tuple of fixture files
        :param models: Models list
        :param operations: Alembic's operations object
        :param selector: Database name in settings.py module
        :return: None
        """

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
        for model in models:
            if model.__tablename__ in table_data:  # type: ignore
                data = table_data[model.__tablename__]  # type: ignore
                operations.bulk_insert(model.__table__, data)  # type: ignore
                for record in data:
                    logger.debug(
                        f"Row {record} added to "  # type: ignore
                        f"table {model.__tablename__}"
                    )
        logger.success(f"Database {selector} populated")

    @staticmethod
    @adapt
    def db_revision(
        config: Config,
        revision: str,
    ) -> None:
        """
        Creates Alembic's revision file in migration directory.

        :param config: Alembic's configuration object
        :param revision: Parent revision

        :return: None
        """
        command.revision(
            config,
            autogenerate=True,
            head=revision,
        )
        logger.success("Revision created")

    @staticmethod
    @adapt
    def db_upgrade(
        config: Config,
        revision: str,
        selector: str,
    ) -> None:
        """
        Applies migration file to a database.

        :param config: Alembic's configuration object
        :param revision: Revision to apply to database
        :param selector: Database name in settings.py module
        :return: None
        """
        command.upgrade(config, revision)
        logger.success(f"Database {selector} upgraded")

    @staticmethod
    def project_setup(name: str, path: str) -> None:
        """
        Creates a project directory with all needed files.

        :param name: Project's name
        :param path: Path to project files
        :return: None
        :raises BasicManagerException:
        """

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

    @staticmethod
    @show_observer_catalogue
    def observe_catalogue(**context) -> dict:
        """
        Pass context dict to illuminate.decorators.cli.show_observe_catalogue.

        :return: dict
        """
        return context

    @show_logo
    @show_info
    def observe_start(self) -> None:
        """
        Starts producer/consumer ETL process.

        :return: None
        """
        io_loop = ioloop.IOLoop.current()
        io_loop.run_sync(self._observe_start)

    async def __start(self) -> None:
        """
        Initializes Adapters and Observers and pass initial Observation
        objects to self.__observation.

        :return: None
        """
        for adapter in self.adapters:
            self._adapters.append(adapter(manager=self))
            logger.opt(colors=True).info(
                f"Adapter <yellow>{adapter.__name__}</yellow> initialized"
            )

        for observer in self.observers:
            instance = observer(manager=self)
            self._observers.append(instance)
            logger.opt(colors=True).info(
                f"Observer <yellow>{observer.__name__}</yellow> initialized"
            )
            for _observation in instance.initial_observations:
                await self.__router(_observation)

    async def __router(
        self, item: Union[Exporter, Finding, Observation]
    ) -> None:
        """
        Routes object based on its class to proper queue.

        :param item: Exporter, Finding or Observation object
        :return: None
        """
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
            _hash = hash(item)
            if _hash not in self.__observing:
                self.__observing.add(_hash)
                if isinstance(item, HTTPObservation) and not item.allowed:
                    return
                await self.__observe_queue.put(item)
        else:
            logger.warning(
                f"Manager rejected item {item} due to unsupported "
                f"item type {type(item)}"
            )

    @logger.catch
    async def __observe(self) -> None:
        """
        Takes Observation object from self.__observe_queue and, after delay,
        pass it to self.__observation method.

        :return: None
        """
        async for item in self.__observe_queue:
            if not item:
                return
            await asyncio.sleep(
                self.settings.OBSERVATION_CONFIGURATION["delay"]
            )
            await self.__observation_switch(item)
            logger.debug(f"Coroutine observed {item}")
            del item
            self.__observe_queue.task_done()

    async def __observe_file(self, item: FileObservation) -> None:
        """
        Calls FileObservation's observe method and pass result to resolve
        function.

        :param item: FileObservation object
        :return: None
        """
        async with item.observe(xcom=item.xcom) as result:
            await self.__observation_resolve(result, item.url)

    async def __observe_http(self, item: HTTPObservation) -> None:
        """
        Prepares HTTPObservation configuration, calls observe method and pass
        result to resolve function.

        :param item: HTTPObservation object
        :return: None
        """
        item.configuration = {
            **self.settings.OBSERVATION_CONFIGURATION["http"],
            **item.configuration,
        }
        result = await item.observe(xcom=item.xcom)
        await self.__observation_resolve(result, item.url)

    async def __observe_sql(self, item: SQLObservation) -> None:
        """
        Calls SQLObservation's observe method and pass result to resolve
        function.

        :param item: SQLObservation object
        :return: None
        """
        result = await item.observe(self.sessions[item.url], xcom=item.xcom)
        await self.__observation_resolve(result, f"{item.url}:{item.query}")

    async def __observe_splash(self, item: SplashObservation) -> None:
        """
        Prepares SplashObservation configuration, calls observe method and pass
        result to resolve function.

        :param item: SplashObservation object
        :return: None
        """
        item.configuration = {
            **self.settings.OBSERVATION_CONFIGURATION["splash"],
            **item.configuration,
        }
        result = await item.observe(
            self.settings.OBSERVATION_CONFIGURATION["http"], xcom=item.xcom
        )
        await self.__observation_resolve(result, item.url)

    async def __observation_resolve(
        self, result: Union[None, Result], url: str
    ):
        """
        Resolves Observation.

        :param result: Result
        :param url: URL str
        :return: None
        """
        if not result:
            self.__not_observed.add(url)
            return
        self.__observed.add(url)
        try:
            if inspect.isawaitable(result):
                await result
            if inspect.isasyncgen(result):
                async for _item in result:
                    await self.__router(_item)
        except Exception:  # noqa
            stack = f"<red>{traceback.format_exc().strip()}</red>"
            logger.opt(colors=True).warning(
                f"Observation callback throws the following exception\n{stack}"
            )

    async def __observation_switch(self, item: Observation) -> None:
        """
        Passes Observation object to proper method based on its class.

        :param item: Observation object
        :return: None
        """
        if isinstance(item, HTTPObservation):
            if isinstance(item, SplashObservation):
                await self.__observe_splash(item)
            else:
                await self.__observe_http(item)
        elif isinstance(item, FileObservation):
            await self.__observe_file(item)
        elif isinstance(item, SQLObservation):
            await self.__observe_sql(item)
        else:
            logger.warning(
                f"Observation of a type {type(item)} is not supported"
            )

    @logger.catch
    async def __adapt(self) -> None:
        """
        Takes Finding object from self.__adapt_queue and pass it to
        self.__adaptation method.

        :return: None
        """
        async for item in self.__adapt_queue:
            if not item:
                return
            await self.__adaptation(item)
            logger.debug(f"Coroutine adapted {item}")
            del item
            self.__adapt_queue.task_done()

    async def __adaptation(self, item: Finding) -> None:
        """
        Passes Finding object to Adapter's instance adapt method.

        :param item: Finding object
        :return: None
        """
        for adapter in self._adapters:
            for subscriber in adapter.subscribers:
                if isinstance(item, subscriber):
                    items = adapter.adapt(item)
                    async for _item in items:  # type: ignore
                        await self.__router(_item)

    @logger.catch
    async def __export(self) -> None:
        """
        Takes Exporter object from self.__export_queue and pass it to
        self.__exportation method.

        :return: None
        """
        async for item in self.__export_queue:
            if not item:
                return
            await self.__export_to(item)
            logger.debug(f"Coroutine exported {item}")
            del item
            self.__export_queue.task_done()

    async def __export_to(self, item: Exporter) -> None:
        """
        Passes Exporter object to proper method based on its class.

        :param item: Exporter object
        :return: None
        """
        if isinstance(item, (InfluxDBExporter, SQLExporter)):
            await self.__export_to_database(item)

    async def __export_to_database(
        self, item: Union[InfluxDBExporter, SQLExporter]
    ) -> None:
        """
        Acquires database session based on Exporter's attributes and pass it to
        Exporter's export method.

        :param item: InfluxDBExporter or SQLExporter object
        :return: None
        """
        try:
            session = self.sessions[item.name]
            await item.export(session)
            self.__exported.add(item)
        except BasicExporterException:
            pass
        except KeyError:
            logger.critical(f"Database {item.name} of is not found in context")

    @logger.catch
    async def _observe_start(self) -> None:
        """
        Starts producer/consumer ETL process.

        :return: None
        """
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

        for session in self.sessions:
            if isinstance(self.sessions[session], InfluxDBClient):
                await self.sessions[session].close()  # type: ignore
