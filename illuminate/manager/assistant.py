from __future__ import annotations

import importlib.util
import inspect
import os
import sys
from pydoc import locate
from types import ModuleType
from typing import Optional, Type, Union

from aioinflux import InfluxDBClient  # type: ignore
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from illuminate.adapter import Adapter
from illuminate.common import SUPPORTED_NOSQL_DATABASES
from illuminate.common import SUPPORTED_SQL_DATABASES
from illuminate.exceptions import BasicManagerException
from illuminate.interface import IAssistant
from illuminate.observer import Observer


class Assistant(IAssistant):
    """
    Assistant class, creates objects from project files.

    Used by Manager class in its static methods and cli start function to
    initialize Manager.
    """

    @staticmethod
    def provide_alembic_config(
        path: str, selector: str, url: Optional[str] = None
    ) -> Config:
        """
        Creates Alembic's configuration object.

        :param path: Migration directory path
        :param selector: Database name in settings.py module DB attribute
        :param url: SQLAlchemy Database URL
        :return: Alembic configuration object
        """
        if not url:
            url = Assistant._provide_db_url(selector)
        config = Config()
        config.set_main_option(
            "script_location", os.path.join(path, "migrations")
        )
        config.set_main_option("sqlalchemy.url", url)
        return config

    @staticmethod
    def provide_alembic_operations(
        selector: str, url: Optional[str] = None
    ) -> Operations:
        """
        Creates Alembic's operations object.
        NOTE: Currently unused after switching to SQLAlchemy 2.0.31. Alembic's
        Operations.bulk_insert is not working at the time of this note
        creation. Still, bulk_insert is considered the proper way to populate
        tables and should be used again when this issue is resolved.

        :param selector: Database name in settings.py module DB attribute
        :param url: SQLAlchemy Database URL
        :return: Alembic operations object
        """
        if not url:
            url = Assistant._provide_db_url(selector)
        engine = create_engine(url)
        context = MigrationContext.configure(engine.connect())
        return Operations(context)

    @staticmethod
    def provide_context(
        sessions: bool = True,
        _labels: Optional[tuple[dict]] = None,
        _observers: Optional[tuple[str]] = None,
    ) -> dict[
        str,
        Union[
            dict[str, Union[sessionmaker[AsyncSession], InfluxDBClient]],
            str,
            list[Union[Type[Adapter], Type[Observer]]],
            ModuleType,
        ],
    ]:
        """
        Creates Manager's constructor kwargs.

        :param sessions: Sessions option
        :param _labels: Optional tuple of Observer's names or class names
        :param _observers: Optional tuple of Observer's names or class names
        :return: Manager's constractor parameters
        :raises BasicManagerException:
        """
        settings = Assistant._provide_settings()
        context = {
            "adapters": Assistant._collect_classes("adapters"),
            "name": settings.NAME,
            "observers": Assistant._collect_classes("observers"),
            "path": os.getcwd(),
            "settings": settings,
        }

        if sessions:
            context["sessions"] = Assistant._provide_sessions()

        if _labels:
            required_labels = {k: v for d in _labels for k, v in d.items()}
            context["observers"] = list(
                filter(
                    lambda x: all(
                        x.LABELS.get(k) == v
                        for k, v in required_labels.items()
                    ),
                    context["observers"],
                )
            )

        if _observers:
            context["observers"] = list(
                filter(
                    lambda x: x.NAME in _observers  # type: ignore
                    or x.__name__ in _observers,
                    context["observers"],
                )
            )

        if not context["observers"]:
            raise BasicManagerException(
                "No observers found or left after filtering"
            )

        return context

    @staticmethod
    def provide_models() -> list[object]:
        """
        Gathers project models.

        :return: Models list
        """
        settings = Assistant._provide_settings()
        return [locate(i) for i in settings.MODELS]

    @staticmethod
    def _collect_classes(
        directory: str,
    ) -> list[Union[Type[Adapter], Type[Observer]]]:
        """
        Recursively collects all classes from a given directory matching its
        prefix (Adapter/Observer).

        :param directory: Either "adapters" or "observers"
        :return: List of matching class types
        """
        classes = []
        prefix = directory.capitalize()[:-1]
        base_dir = os.path.join(os.getcwd(), directory)

        for dirpath, _, filenames in os.walk(base_dir):
            for filename in filenames:
                if not filename.endswith(".py") or filename.startswith(
                    "__init__"
                ):
                    continue

                full_path = os.path.join(dirpath, filename)
                rel_path = os.path.relpath(full_path, os.getcwd())

                module_name = rel_path.replace(os.sep, ".")[:-3]
                spec = importlib.util.spec_from_file_location(
                    module_name, full_path
                )

                if not spec or not spec.loader:
                    continue

                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                for name, cls in inspect.getmembers(module, inspect.isclass):
                    if cls.__module__ != module_name:
                        continue
                    if name.startswith(prefix) and len(name) > len(prefix):
                        classes.append(cls)

        return classes

    @staticmethod
    def _provide_db_url(selector: str, _async: bool = False) -> str:
        """
        Creates database URL.

        :param selector: Database name in settings.py module DB attribute
        :param _async: Async URL flag
        :return: Database URL string
        :raises BasicManagerException:
        """
        settings = Assistant._provide_settings()
        try:
            db = settings.DB[selector]
        except KeyError:
            raise BasicManagerException(
                f"Database {selector} is not defined in settings.py"
            )
        if not db.get("name"):
            db["name"] = settings.NAME
        if _async:
            async_drivers = {
                "mysql": "asyncmy",
                "postgresql": "asyncpg",
            }
            driver = async_drivers[db["type"]]
            return "{type}+{driver}://{user}:{pass}@{host}/{name}".format(
                driver=driver, **db
            )

        return "{type}://{user}:{pass}@{host}/{name}".format(**db)

    @staticmethod
    def _provide_sessions() -> (
        dict[str, Union[sessionmaker[AsyncSession], InfluxDBClient]]
    ):
        """
        Creates a dictionary of database sessions.

        :return: Database sessions dictionary
        """
        _sessions: dict = {}
        settings = Assistant._provide_settings()
        logger.opt(colors=True).info(
            f"Number of expected db connections: "
            f"<yellow>{len(settings.DB)}</yellow>"
        )
        for db in settings.DB:
            _type = settings.DB[db]["type"]
            if _type in SUPPORTED_NOSQL_DATABASES:
                session = Assistant.__provide_nosql_sessions(db, settings)
                _sessions.update({db: session})
            elif _type in SUPPORTED_SQL_DATABASES:
                session = Assistant.__provide_sql_sessions(db, settings)
                _sessions.update({db: session})
            else:
                logger.warning(f"Database type {_type} is not supported")

        return _sessions

    @staticmethod
    def _provide_settings() -> ModuleType:
        """
        Imports project's settings.py module and returns it.

        :return: Project's settings.py module
        :raises BasicManagerException:
        """
        try:
            import settings  # type: ignore

            return settings
        except ImportError:
            raise BasicManagerException(
                "Framework did not found settings.py in the current directory"
            )

    @staticmethod
    def __log_database_connection(db: str, settings: ModuleType) -> None:
        """
        Log database connection.

        :param db: database name from settings.py module
        :param settings: settings.py module
        :return: None
        """
        host = settings.DB[db]["host"]
        port = settings.DB[db]["port"]
        logger.opt(colors=True).info(
            f"Adding session with <yellow>{db}</yellow> at "
            f"<magenta>{host}:{port}</magenta> to context"
        )

    @staticmethod
    def __provide_nosql_sessions(
        db: str, settings: ModuleType
    ) -> InfluxDBClient:
        """
        Provides NoSQL database session.

        :param db: database name from settings.py module
        :param settings: settings.py module
        :return: InfluxDBClient object
        """
        Assistant.__log_database_connection(db, settings)
        if settings.DB[db]["type"] == "influxdb":
            return InfluxDBClient(
                host=settings.DB[db]["host"],
                port=settings.DB[db]["port"],
                db=settings.DB[db].get("name", settings.NAME),
                username=settings.DB[db]["user"],
                password=settings.DB[db]["pass"],
            )
        return None

    @staticmethod
    def __provide_sql_sessions(
        db: str, settings: ModuleType
    ) -> sessionmaker[AsyncSession]:
        """
        Provides SQL database session.

        :param db: database name from settings.py module
        :param settings: settings.py module
        :return: AsyncSession created with session maker
        """
        Assistant.__log_database_connection(db, settings)
        return sessionmaker(
            create_async_engine(Assistant._provide_db_url(db, _async=True)),
            class_=AsyncSession,
            expire_on_commit=False,
        )
