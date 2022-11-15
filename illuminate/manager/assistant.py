from __future__ import annotations

import importlib.util
import inspect
import os
import sys
from types import ModuleType
from typing import Optional, Type, Union

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from illuminate.adapter.adapter import Adapter
from illuminate.exceptions.manager import BasicManagerException
from illuminate.interface.assistant import IAssistant
from illuminate.observer.observer import Observer


class Assistant(IAssistant):
    """
    Assistant class, creates objects from project files.

    Used by Manager class in its static methods and cli start function to
    initialize Manager.
    """

    @staticmethod
    def create_alembic_config(
        path: str, selector: str, url: Optional[str]
    ) -> Config:
        """
        Creates Alembic's configuration object.

        :param path: Migration directory path
        :param selector: Database name in settings.py module DB attribute
        :param url: SQLAlchemy Database URL
        :return: Alembic configuration object
        """
        if not url:
            url = Assistant.create_db_url(selector)
        config = Config()
        config.set_main_option(
            "script_location", os.path.join(path, "migrations")
        )
        config.set_main_option("sqlalchemy.url", url)
        return config

    @staticmethod
    def create_db_url(selector: str, _async: bool = False) -> str:
        """
        Creates database URL.

        :param selector: Database name in settings.py module DB attribute
        :param _async: Async URL flag
        :return: Database URL string
        """
        settings = Assistant.import_settings()
        db = settings.DB[selector]
        db["db"] = settings.NAME
        if _async:
            async_drivers = {
                "mysql": "asyncmy",
                "postgresql": "asyncpg",
            }
            driver = async_drivers[db["type"]]
            return "{type}+{driver}://{user}:{pass}@{host}/{db}".format(
                driver=driver, **db
            )
        return "{type}://{user}:{pass}@{host}/{db}".format(**db)

    @staticmethod
    def import_settings() -> ModuleType:
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
    def provide_context(
        _filter: Optional[tuple[str]] = None,
    ) -> dict[
        str, Union[str, list[Union[Type[Observer], Type[Adapter]]], ModuleType]
    ]:
        """
        Creates Manager's constructor kwargs.

        :param _filter: Optional tuple of Observer's names or class names
        :return: Manager's contractor parameters
        :raises BasicManagerException:
        """
        settings = Assistant.import_settings()
        context = {
            "adapters": [],
            "name": settings.NAME,
            "observers": [],
            "path": os.getcwd(),
            "sessions": Assistant.provide_sessions(),
            "settings": settings,
        }

        for folder in ("adapters", "observers"):
            directory = os.path.join(os.getcwd(), folder)
            files = [
                f
                for f in next(os.walk(directory))[2]
                if f.endswith(".py") and not f.startswith("__init__")
            ]
            for file in files:
                _module = f"{folder}.{file}"
                spec = importlib.util.spec_from_file_location(
                    _module, os.path.join(directory, file)
                )
                module = importlib.util.module_from_spec(spec)  # type: ignore
                sys.modules[_module] = module
                spec.loader.exec_module(module)  # type: ignore

                for name, cls in inspect.getmembers(module, inspect.isclass):
                    proper_class = name.startswith(folder.capitalize()[:-1])
                    basic_import = len(name) == len(folder[:-1])
                    if proper_class and not basic_import:
                        context[folder].append(cls)

        if _filter:
            context["observers"] = list(
                filter(
                    lambda x: x.NAME in _filter  # type: ignore
                    or x.__name__ in _filter,
                    context["observers"],
                )
            )

        if not context["observers"]:
            raise BasicManagerException(
                "No observers found or left after filtering"
            )

        return context

    @staticmethod
    def provide_sessions() -> dict[str, dict[str, Type[AsyncSession]]]:
        """
        Creates a dictionary of database sessions.

        :return: None
        """
        _sessions: dict[str, dict[str, Type[AsyncSession]]] = {
            "mysql": {},
            "postgresql": {},
        }
        settings = Assistant.import_settings()
        logger.opt(colors=True).info(
            f"Number of expected db connections: "
            f"<yellow>{len(settings.DB)}</yellow>"
        )
        for db in settings.DB:
            _type = settings.DB[db]["type"]
            if _type in ("mysql", "postgresql"):
                url = Assistant.create_db_url(db, _async=True)
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
                _sessions[_type] = {db: session}  # type: ignore
        return _sessions

    @staticmethod
    def provide_alembic_operations(
        selector: str, url: Optional[str]
    ) -> Operations:
        """
        Creates Alembic's operations object.

        :param selector: Database name in settings.py module DB attribute
        :param url: SQLAlchemy Database URL
        :return: Alembic operations object
        """
        if not url:
            url = Assistant.create_db_url(selector)
        engine = create_engine(url)
        context = MigrationContext.configure(engine.connect())
        return Operations(context)
