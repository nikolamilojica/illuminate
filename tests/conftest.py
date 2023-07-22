import asyncio
import io

import pytest
from tornado.httpclient import HTTPClientError
from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPResponse

FETCH = "tornado.httpclient.AsyncHTTPClient.fetch"
URL = "https://example.com"


@pytest.fixture(scope="function")
def async_http_response_ok(mocker):
    """
    Patch fetch function to return predefined response object.
    """
    future = asyncio.Future()
    request = HTTPRequest(URL)
    response = HTTPResponse(request, 200, None, io.BytesIO(b'{"data": true}'))
    future.set_result(response)
    mocker.patch(FETCH, return_value=future)


@pytest.fixture(scope="function")
def async_http_response_not_ok(mocker):
    """
    Patch fetch function to raise HTTPClientError.
    """

    def _side_effect(*args, **kwargs):
        raise HTTPClientError(509, "Timeout", None)

    future = asyncio.Future()
    future.set_result(_side_effect)
    mocker.patch(FETCH, side_effect=_side_effect)


@pytest.fixture(scope="function")
def async_influxdb_write(mocker):
    """
    Patch write function to return True.
    """

    future = asyncio.Future()
    future.set_result(True)
    mocker.patch("aioinflux.InfluxDBClient.write", return_value=future)
