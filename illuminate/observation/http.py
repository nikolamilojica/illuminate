from __future__ import annotations

import urllib.parse
from collections.abc import AsyncGenerator
from copy import copy
from typing import Callable, Optional, Union

from loguru import logger
from tornado import httpclient
from tornado.httpclient import HTTPClientError
from tornado.httpclient import HTTPResponse

from illuminate.exporter import Exporter
from illuminate.observation import Observation
from illuminate.observer import Finding


class HTTPObservation(Observation):
    """
    HTTPObservation class, reads data from HTTP server asynchronously. Inherits
    Observation class and implements observe method.
    """

    def __hash__(self) -> int:
        """
        HTTPObservation object hash value.

        :return: int
        """
        body = self.configuration.get("body")
        method = self.configuration.get("method")
        return hash(f"{method}|{self.url}|:{body}")

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
        """
        HTTPObservation's __init__ method.

        :param url: Data's HTTP URL
        :param allowed: Collection of strings evaluated against self.url to
        determent if URL is allowed
        :param callback: Async function/method that will manipulate response
        object and yield Exporter, Finding and Observation objects
        """
        super().__init__(url)
        self._allowed = allowed
        self._callback = callback
        self.configuration = kwargs

    @property
    def allowed(self) -> bool:
        """
        Checks if HTTP URL is allowed to be requested.

        :return: bool
        """
        for allowed in self._allowed:
            if self.url.startswith(allowed):
                return True
        return False

    async def observe(
        self, *args, **kwargs
    ) -> Optional[AsyncGenerator[Union[Exporter, Finding, Observation], None]]:
        """
        Requests data from HTTP server, passes response object to a callback
        and returns async Exporter, Finding, and Observation object generator
        if request is successful.

        :return: Async Exporter, Finding, and Observation object generator or
        None
        """
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
            return None

    def __repr__(self):
        """
        HTTPObservation's __repr__ method.

        :return: String representation of an instance
        """
        return f'HTTPObservation("{self.url}",callback="{self._callback}")'


class SplashObservation(HTTPObservation):
    """
    SplashObservation class, reads data from HTTP server asynchronously.
    Inherits HTTPObservation class and implements observe method.

    Constructor's kwargs are used to create Splash service URL. For full list
    of parameters visit https://splash.readthedocs.io/en/stable/api.html.

    Note: URL is passed as positional argument. It will be used as param
    in Splash service URL.
    """

    def __hash__(self) -> int:
        """
        SplashObservation object hash value.

        :return: int
        """
        return hash(self.service)

    @property
    def service(self):
        """
        Constructs URL of Splash service

        :return: Splash URL string
        """
        parameters = copy(self.configuration)
        host = parameters.pop("host")
        port = parameters.pop("port")
        protocol = parameters.pop("protocol")
        parameters["url"] = self.url
        render = parameters.pop("render")
        return (
            f"{protocol}://{host}:{port}/render.{render}?"
            f"{urllib.parse.urlencode(parameters)}"
        )

    async def observe(
        self, configuration: dict, *args, **kwargs
    ) -> Optional[AsyncGenerator[Union[Exporter, Finding, Observation], None]]:
        """
        Requests data from HTTP server and renders response with Splash, passes
        response object to a callback and returns async Exporter, Finding, and
        Observation object generator if request is successful.

        :param configuration: HTTP configuration dict from settings.py
        :return: Async Exporter, Finding, and Observation object generator or
        None
        """
        try:
            response = await httpclient.AsyncHTTPClient().fetch(
                self.service, **configuration
            )
            logger.info(f"{self}.observe() -> {response}")
            return self._callback(response, *args, **kwargs)
        except HTTPClientError as exception:
            logger.warning(f"{self}.observe() -> {exception}")
            return None
        except Exception as exception:
            logger.critical(f"{self}.observe() -> {exception}")
            return None

    def __repr__(self):
        """
        SplashObservation's __repr__ method.

        :return: String representation of an instance
        """
        return f'SplashObservation("{self.url}",callback="{self._callback}")'
