from __future__ import annotations

import importlib.util
import inspect
import os
import sys
from types import ModuleType
from typing import Optional, Type, Union

from alembic.config import Config
from loguru import logger

from illuminate.adapter.adapter import Adapter
from illuminate.exceptions.manager import BasicManagerException
from illuminate.interface.assistant import IAssistant
from illuminate.observer.observer import Observer


class Assistant(IAssistant):
    """Assistant class, responsible for assisting Manager class"""

    @staticmethod
    @logger.catch
    def create_alembic_config(path: str, url: str) -> Config:
        """Creates config object needed to perform Alembic commands"""
        config = Config()
        config.set_main_option(
            "script_location", os.path.join(path, "migrations")
        )
        config.set_main_option("sqlalchemy.url", url)
        return config

    @staticmethod
    def create_db_url(
        selector: str, settings: ModuleType, _async: bool = False
    ) -> str:
        """Creates db url from data in settings.py module"""
        db = settings.DB[selector]
        db["db"] = settings.NAME
        if _async:
            async_drivers = {"postgresql": "asyncpg"}
            driver = async_drivers[db["type"]]
            return "{type}+{driver}://{user}:{pass}@{host}/{db}".format(
                driver=driver, **db
            )
        return "{type}://{user}:{pass}@{host}/{db}".format(**db)

    @staticmethod
    def import_settings() -> ModuleType:
        """Tries to import project settings.py module and returns it"""
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
        """Provides context for the current run"""
        settings = Assistant.import_settings()
        context = {
            "adapters": [],
            "name": settings.NAME,
            "observers": [],
            "path": os.getcwd(),
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
