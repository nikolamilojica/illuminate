from loguru import logger
from tornado import httpclient
from tornado.httpclient import HTTPClientError

from illuminate.exceptions.observation import BasicObservationException
from illuminate.observation.observation import Observation


class HTTPObservation(Observation):
    """HTTPObservation class, responsible for reading source with callback"""

    def __init__(self, url, /, allowed, callback, *args, **kwargs):
        self.url = url
        self._allowed = allowed
        self._callback = callback
        self.configuration = kwargs

    @property
    def allowed(self):
        for allowed in self._allowed:
            if self.url.startswith(allowed):
                return True
        return False

    async def observe(self, *args, **kwargs):
        """Read source and use observer's callback function against response"""
        try:
            response = await httpclient.AsyncHTTPClient().fetch(
                self.url, **self.configuration
            )
            logger.info(f"{self}.observe() -> {response}")
            return self._callback(response, *args, **kwargs)
        except HTTPClientError as exception:
            logger.warning(f"{self}.observe() -> {exception}")
            return
        except Exception as exception:
            logger.critical(f"{self}.observe() -> {exception}")
            raise BasicObservationException

    def __repr__(self):
        return f'HTTPObservation("{self.url}",callback="{self._callback}")'
