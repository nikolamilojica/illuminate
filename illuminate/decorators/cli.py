from __future__ import annotations

import functools
from typing import Callable

from loguru import logger
from sqlalchemy.exc import NoSuchModuleError

from illuminate.exceptions import BasicManagerException
from illuminate.manager import Assistant


def adapt(command: str) -> Callable:
    """
    Adapts Manager's static methods to accept cli arguments.

    :param command: Command string
    :return: Manager's static method wrapper
    """

    def decorator(func: Callable) -> Callable:
        """
        Outer wrapper responsible for control flow.

        :param func: The function to be adapted
        :return: The wrapped function with adapted arguments
        """

        if command == "populate":

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

                try:
                    func(
                        fixtures,
                        selector,
                        url or Assistant._provide_db_url(selector),
                        *args,
                        **kwargs,
                    )
                except NoSuchModuleError:
                    raise BasicManagerException(
                        "Command populate can only be performed on SQL "
                        f"database, {selector} is not supported SQL database"
                    )

        elif command == "revision":

            @functools.wraps(func)
            def wrapper(
                path: str,
                revision: str,
                selector: str,
                url: str,
                *args,
                **kwargs,
            ) -> None:
                """
                Adapts Manager's db_revision method to accept cli arguments.

                :param path: Migration directory path
                :param revision: Parent revision
                :param selector: Database name in settings.py module
                :param url: SQLAlchemy Database URL
                :return: None
                """
                try:
                    config = Assistant.provide_alembic_config(
                        path, selector, url
                    )
                    func(config, revision, *args, **kwargs)
                except NoSuchModuleError:
                    raise BasicManagerException(
                        "Command revision can only be performed on SQL "
                        f"database, {selector} is not supported SQL database"
                    )

        elif command == "upgrade":

            @functools.wraps(func)
            def wrapper(
                path: str,
                revision: str,
                selector: str,
                url: str,
                *args,
                **kwargs,
            ) -> None:
                """
                Adapts Manager's db_upgrade method to accept cli arguments.

                :param path: Migration directory path
                :param revision: Parent revision
                :param selector: Database name in settings.py module
                :param url: SQLAlchemy Database URL
                :return: None
                """
                try:
                    config = Assistant.provide_alembic_config(
                        path, selector, url
                    )
                    func(config, revision, selector, *args, **kwargs)
                except NoSuchModuleError:
                    raise BasicManagerException(
                        "Command upgrade can only be performed on SQL "
                        f"database, {selector} is not supported SQL database"
                    )

        else:
            logger.warning(f"Decorated command {command} is not supported")

            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> None:
                """
                Does nothing.

                :return: None
                """
                func(*args, **kwargs)

        return wrapper

    return decorator
