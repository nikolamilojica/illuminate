from __future__ import annotations

from typing import Type, TypeVar

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from illuminate.exceptions.exporter import BasicExporterException
from illuminate.exporter.exporter import Exporter

M = TypeVar("M")


class SQLExporter(Exporter):
    """SQLExporter class, responsible for writing to destination"""

    name: str
    type: str

    def __init__(self, model: M):
        self.model = model

    async def export(
        self, session: Type[AsyncSession], *args, **kwargs
    ) -> None:
        """Load to destination"""
        async with session() as session:  # type: ignore
            async with session.begin():  # type: ignore
                session.add(self.model)  # type: ignore
                try:
                    await session.commit()  # type: ignore
                except Exception as exception:
                    logger.critical(
                        f'{self}.export(session="{session}") -> {exception}'
                    )
                    raise BasicExporterException
        logger.success(f'{self}.export(session="{session}")')

    def __repr__(self):
        return f"SQLExporter(model={self.model})"
