from __future__ import annotations

import functools
import inspect
from typing import Callable

from loguru import logger

from illuminate.manager.assistant import Assistant


def adapt(func: Callable) -> Callable:
    """
    Adapts Manager's static methods to accept cli arguments.

    :param func: Manager's static method
    :return: Manager's static method wrapper
    """

    _callable = inspect.stack()[1][4][0]  # type: ignore
    _callable = _callable.strip().split(" ")[1].split("(")[0]

    if _callable == "db_populate":

        @functools.wraps(func)
        def wrapper(
            fixtures: tuple[str], selector: str, url: str, *args, **kwargs
        ) -> None:
            """
            Adapts Manager's db_populate method to accept cli arguments.

            :param fixtures: Tuple of fixture files
            :param selector: Database name in settings.py module
            :param url: SQLAlchemy Database URL
            :return: None
            """
            models = Assistant.provide_models()
            operations = Assistant.provide_alembic_operations(selector, url)
            func(fixtures, models, operations, selector, *args, **kwargs)

    elif _callable == "db_revision":

        @functools.wraps(func)
        def wrapper(
            path: str, revision: str, selector: str, url: str, *args, **kwargs
        ) -> None:
            """
            Adapts Manager's db_revision method to accept cli arguments.

            :param path: Migration directory path
            :param revision: Parent revision
            :param selector: Database name in settings.py module
            :param url: SQLAlchemy Database URL
            :return: None
            """
            config = Assistant.provide_alembic_config(path, selector, url)
            func(config, revision, *args, **kwargs)

    elif _callable == "db_upgrade":

        @functools.wraps(func)
        def wrapper(
            path: str, revision: str, selector: str, url: str, *args, **kwargs
        ) -> None:
            """
            Adapts Manager's db_upgrade method to accept cli arguments.

            :param path: Migration directory path
            :param revision: Parent revision
            :param selector: Database name in settings.py module
            :param url: SQLAlchemy Database URL
            :return: None
            """
            config = Assistant.provide_alembic_config(path, selector, url)
            func(config, revision, selector, *args, **kwargs)

    else:
        logger.warning(f"Decorated method {_callable} is not supported")

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> None:
            """
            Does nothing.

            :return: None
            """
            func(*args, **kwargs)

    return wrapper
