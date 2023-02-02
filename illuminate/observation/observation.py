from __future__ import annotations

from typing import Any

from illuminate.exceptions import BasicObservationException
from illuminate.interface import IObservation


class Observation(IObservation):
    """
    Observation class, reads data from the source. Class must be inherited and
    method observe must be implemented in a child class.
    """

    def __hash__(self):
        """
        Observation object hash value.

        :return: None
        :raises BasicObservationException:
        """
        raise BasicObservationException(
            "Property hash must be implemented in child class"
        )

    def __init__(self, url: Any):
        """
        Observation's __init__ method.

        :param url: Data's URL
        """
        self.url = url

    async def observe(self, *args, **kwargs):
        """
        Reads data from the source. Must be implemented in a child class.

        :return: None
        :raises BasicObservationException:
        """
        raise BasicObservationException(
            "Method observe must be implemented in child class"
        )
