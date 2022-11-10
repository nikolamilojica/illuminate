from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Union

from tornado.httpclient import HTTPResponse

from illuminate.exceptions.observer import BasicObserverException
from illuminate.exporter.exporter import Exporter
from illuminate.interface.observer import IObserver
from illuminate.observation.observation import Observation
from illuminate.observer.finding import Finding


class Observer(IObserver):
    """Observer class, responsible for producing observations and findings"""

    NAME: str

    def __init__(self):
        self.initial_observations: list[Observation] = []

    async def observe(
        self, response: HTTPResponse, *args, **kwargs
    ) -> AsyncGenerator[Union[Exporter, Finding, Observation], None]:
        """Extract observations and/or findings from response"""
        raise BasicObserverException(
            "Method observe must be implemented in child class"
        )
