from tornado import httpclient

from illuminate.observation.observation import Observation


class HTTPObservation(Observation):
    def __init__(self, allowed, url, callback):
        self._allowed = allowed
        self.url = url
        self._callback = callback

    @property
    def allowed(self):
        for allowed in self._allowed:
            if self.url.startswith(allowed):
                return True
        return False

    async def extract(self, *args, **kwargs):
        """Read source and use observer's callback function against response"""
        try:
            response = await httpclient.AsyncHTTPClient().fetch(self.url)
            # TODO: log response
            return self._callback(response, *args, **kwargs)
        except Exception as exception:
            # TODO: narrow down exceptions and log them
            return None
