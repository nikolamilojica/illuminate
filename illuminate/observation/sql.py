from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Callable, Optional, Type, Union

from loguru import logger
from sqlalchemy.engine.result import Result
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.sql.selectable import Select

from illuminate.exporter import Exporter
from illuminate.observation import Observation
from illuminate.observer import Finding


class SQLObservation(Observation):
    """
    SQLObservation class, reads data from database asynchronously. Inherits
    Observation class and implements observe method.
    """

    def __hash__(self) -> int:
        """
        SQLObservation object hash value.

        :return: int
        """
        query = str(self.query)
        return hash(f"{self.url}|:{query}")

    def __init__(
        self,
        query: Union[Select, TextClause],
        url: str,
        /,
        callback: Callable[
            [Result, tuple, dict],
            AsyncGenerator[Union[Exporter, Finding, Observation], None],
        ],
        *args,
        **kwargs,
    ):
        """
        SQLObservation's __init__ method.

        :param query: SQLAlchemy query object.
        :param url: Database name in project settings.
        :param callback: Async function/method that will manipulate response
        object and yield Exporter, Finding and Observation objects
        """
        super().__init__(url)
        self._callback = callback
        self.query = query

    async def observe(
        self, session: Type[AsyncSession], *args, **kwargs
    ) -> Optional[AsyncGenerator[Union[Exporter, Finding, Observation], None]]:
        """
        Reads data from database, passes response object to a callback
        and returns async Exporter, Finding, and Observation object generator
        if request is successful.

        :return: Async Exporter, Finding, and Observation object generator or
        None
        """
        try:
            async with session() as session:  # type: ignore
                async with session.begin():  # type: ignore
                    query = self.query
                    response = await session.execute(query)  # type: ignore
            logger.success(f'{self}.observe(session="{session}")')
            return self._callback(response, *args, **kwargs)
        except SQLAlchemyError as exception:
            logger.warning(f"{self}.observe() -> {exception}")
            return None

    def __repr__(self):
        """
        SQLObservation's __repr__ method.

        :return: String representation of an instance
        """
        return (
            f'SQLObservation("{self.query}","{self.query}",'
            f'callback="{self._callback}")'
        )
