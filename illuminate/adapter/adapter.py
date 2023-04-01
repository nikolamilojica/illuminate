from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Optional, Type, TYPE_CHECKING, Union

from illuminate.exceptions import BasicAdapterException
from illuminate.exporter import Exporter
from illuminate.interface import IAdapter
from illuminate.observation import Observation
from illuminate.observer import Finding

if TYPE_CHECKING:
    from illuminate.manager import Manager


class Adapter(IAdapter):
    """
    Adapter class, generates Exporter and Observation objects using Finding
    instances with optional transformation. Class must be inherited and method
    adapt must be implemented in a child class.
    """

    priority: int
    """
    Place in Adapter list. If two Adapters have the same Finding in subscriber
    tuple, one with the higher priority will call method adapt first on
    Finding object.
    """

    subscribers: tuple[Type[Finding]]
    """
    Tuple of Finding class children used to determent if Adapter object should
    call method adapt on Finding instance.
    """

    def __init__(self, manager: Optional[Manager] = None):
        """
        Adapter's __init__ method.

        :param manager: Manager object
        """
        self.manager = manager

    async def adapt(
        self, finding: Finding, *args, **kwargs
    ) -> AsyncGenerator[Union[Exporter, Observation], None]:
        """
        Generates Exporter and Observation objects. Must be implemented in a
        child class.

        It is meant to be a scope where additional transformation up on
        finding objects should be performed (like data enrichment from
        additional data source) before yielding Exporter or Observation
        instances.

        :param finding: Finding object
        :return: Async Exporter and Observation object generator
        :raises BasicAdapterException:
        """
        raise BasicAdapterException(
            "Method adapt must be implemented in child class"
        )
