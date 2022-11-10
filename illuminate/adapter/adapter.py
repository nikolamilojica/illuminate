from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Type, Union

from illuminate.exceptions.adapter import BasicAdapterException
from illuminate.exporter.exporter import Exporter
from illuminate.interface.adapter import IAdapter
from illuminate.observation.observation import Observation
from illuminate.observer.finding import Finding


class Adapter(IAdapter):
    """Adapter class, responsible for producing exporters"""

    priority: int
    subscribers: tuple[Type[Finding]]

    async def adapt(
        self, finding: Finding, *args, **kwargs
    ) -> AsyncGenerator[Union[Exporter, Observation], None]:
        """Transform finding and produce exporters"""
        raise BasicAdapterException(
            "Method adapt must be implemented in child class"
        )
