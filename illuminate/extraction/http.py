from tornado import httpclient

from illuminate.discrete.extraction.http import Interface


class HTTPExtraction(Interface):
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

    async def callback(self, *args, **kwargs):
        try:
            response = await httpclient.AsyncHTTPClient().fetch(self.url)
            # TODO: log response
            return self._callback(response, *args, **kwargs)
        except Exception as exception:
            # TODO: narrow down exceptions and log them
            return None
