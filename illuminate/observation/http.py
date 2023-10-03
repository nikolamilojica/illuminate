from __future__ import annotations

import urllib.parse
from copy import copy
from typing import Any, Callable, Optional, Union

from loguru import logger
from tornado import httpclient
from tornado.httpclient import HTTPResponse

from illuminate.meta.type import Result
from illuminate.observation import Observation


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
        callback: Callable[[HTTPResponse, tuple, dict], Result],
        xcom: Optional[Any] = None,
        *args,
        **kwargs,
    ):
        """
        HTTPObservation's __init__ method.

        :param url: Data's HTTP URL
        :param allowed: Collection of strings evaluated against self.url to
        determent if URL is allowed
        :param callback: Async function/method that manipulates HTTPResponse
        object and returns Result.
        :param xcom: Cross communication object
        """
        super().__init__(url, xcom=xcom)
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

    async def observe(self, *args, **kwargs) -> Union[None, Result]:
        """
        Requests data from HTTP server, passes response object to a callback
        and returns None or Result.

        :return: None or Result
        """
        try:
            response = await httpclient.AsyncHTTPClient().fetch(
                self.url, **self.configuration
            )
            logger.info(f"{self}.observe() -> {response}")
            return self._callback(response, *args, **kwargs)
        except Exception as exception:
            logger.warning(f"{self}.observe() -> {exception}")
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
        defaults: dict = {
            "host": "localhost",
            "port": 8050,
            "protocol": "http",
            "render": "html",
        }
        parameters = copy(self.configuration)
        for i in defaults:
            if i in parameters:
                defaults[i] = parameters[i]
                del parameters[i]
        parameters["url"] = self.url
        endpoint = "{protocol}://{host}:{port}/render.{render}?"
        endpoint = endpoint.format(**defaults)
        parameters = urllib.parse.urlencode(parameters)
        return f"{endpoint.format(**defaults)}{parameters}"

    async def observe(
        self, configuration: dict, *args, **kwargs
    ) -> Union[None, Result]:
        """
        Requests data from HTTP server and renders response with Splash, passes
        response object to a callback and returns None or Result.

        :param configuration: HTTP configuration dict from settings.py
        :return: None or Result
        """
        try:
            response = await httpclient.AsyncHTTPClient().fetch(
                self.service, **configuration
            )
            logger.info(f"{self}.observe() -> {response}")
            return self._callback(response, *args, **kwargs)
        except Exception as exception:
            logger.warning(f"{self}.observe() -> {exception}")
            return None

    def __repr__(self):
        """
        SplashObservation's __repr__ method.

        :return: String representation of an instance
        """
        return f'SplashObservation("{self.url}",callback="{self._callback}")'
