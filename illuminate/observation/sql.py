from __future__ import annotations

from typing import Any, Callable, Optional, Type, Union

from loguru import logger
from sqlalchemy.engine.result import Result as AlchemyResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import TextClause
from sqlalchemy.sql.selectable import Select

from illuminate.meta.type import Result
from illuminate.observation import Observation


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
        callback: Callable[[AlchemyResult, tuple, dict], Result],
        xcom: Optional[Any] = None,
        *args,
        **kwargs,
    ):
        """
        SQLObservation's __init__ method.

        :param query: SQLAlchemy query object.
        :param url: Database name in project settings.
        :param callback: Async function/method that manipulates AlchemyResult
        object and returns Result.
        :param xcom: Cross communication object
        """
        super().__init__(url, xcom=xcom)
        self._callback = callback
        self.query = query

    async def observe(
        self, session: Type[AsyncSession], *args, **kwargs
    ) -> Union[None, Result]:
        """
        Reads data from database, passes response object to a callback
        and returns None or Result.

        :return: None or Result
        """
        try:
            async with session() as session:  # type: ignore
                async with session.begin():  # type: ignore
                    query = self.query
                    response = await session.execute(query)  # type: ignore
            logger.info(f'{self}.observe(session="{session}")')
            return self._callback(response, *args, **kwargs)
        except Exception as exception:
            logger.warning(f"{self}.observe() -> {exception}")
            return None

    def __repr__(self):
        """
        SQLObservation's __repr__ method.

        :return: String representation of an instance
        """
        return (
            f'SQLObservation("{self.query}","{self.url}",'
            f'callback="{self._callback}")'
        )
