from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Callable, Optional, Union

from loguru import logger
from tornado import httpclient
from tornado.httpclient import HTTPClientError
from tornado.httpclient import HTTPResponse

from illuminate.exceptions.observation import BasicObservationException
from illuminate.exporter.exporter import Exporter
from illuminate.observation.observation import Observation
from illuminate.observer.finding import Finding


class HTTPObservation(Observation):
    """HTTPObservation class, responsible for reading source with callback"""

    def __init__(
        self,
        url: str,
        /,
        allowed: Union[list[str], tuple[str]],
        callback: Callable[
            [HTTPResponse, tuple, dict],
            AsyncGenerator[Union[Exporter, Finding, Observation], None],
        ],
        *args,
        **kwargs,
    ):
        self.url = url
        self._allowed = allowed
        self._callback = callback
        self.configuration = kwargs

    @property
    def allowed(self) -> bool:
        for allowed in self._allowed:
            if self.url.startswith(allowed):
                return True
        return False

    async def observe(
        self, *args, **kwargs
    ) -> Optional[AsyncGenerator[Union[Exporter, Finding, Observation], None]]:
        """Read source and use observer's callback function against response"""
        try:
            response = await httpclient.AsyncHTTPClient().fetch(
                self.url, **self.configuration
            )
            logger.info(f"{self}.observe() -> {response}")
            return self._callback(response, *args, **kwargs)
        except HTTPClientError as exception:
            logger.warning(f"{self}.observe() -> {exception}")
            return None
        except Exception as exception:
            logger.critical(f"{self}.observe() -> {exception}")
            raise BasicObservationException

    def __repr__(self):
        return f'HTTPObservation("{self.url}",callback="{self._callback}")'
