from __future__ import annotations

from typing import Type, TypeVar, Union

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from illuminate.exceptions import BasicExporterException
from illuminate.exporter import Exporter

M = TypeVar("M")


class SQLExporter(Exporter):
    """
    SQLExporter class, writes data to SQL database asynchronously. Inherits
    Exporter class and implements export method.

    Each SQLExporter object is responsible for a single transaction with a
    single database. Attribute name is used to acquire database session object
    from Manager's sessions attribute.

    Supported dialects:
        - Mysql
        - Postgres
    """

    name: str
    """
    SQL database name selector used to get database session object from
    Manager.sessions attribute.
    """

    def __init__(self, models: Union[list[M], tuple[M]]):
        """
        SQLExporter's __init__ method.

        :param models: SQLAlchemy model objects collection
        """
        self.models = models

    async def export(
        self, session: Type[AsyncSession], *args, **kwargs
    ) -> None:
        """
        Writes data to SQL database asynchronously.

        :param session: AsyncSession object
        :return: None
        :raises BasicExporterException:
        """
        async with session() as session:  # type: ignore
            async with session.begin():  # type: ignore
                session.add_all(self.models)  # type: ignore
                try:
                    await session.commit()  # type: ignore
                except Exception as exception:
                    logger.critical(
                        f'{self}.export(session="{session}") -> {exception}'
                    )
                    raise BasicExporterException
        logger.success(f'{self}.export(session="{session}")')

    def __repr__(self):
        """
        SQLExporter's __repr__ method.

        :return: String representation of an instance
        """
        return f"SQLExporter(models={self.models})"
