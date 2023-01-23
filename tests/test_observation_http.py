import asyncio
import io
import json

import pytest
from tornado.httpclient import HTTPClientError
from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPResponse

from illuminate.exceptions import BasicObservationException
from illuminate.observation import HTTPObservation


class TestSQLExporterClass:

    function = "tornado.httpclient.AsyncHTTPClient.fetch"
    url = "https//:example.com"

    @staticmethod
    @pytest.fixture(scope="function")
    def async_http_response_ok(mocker):
        """
        Patch fetch function to return predefined response object.
        """
        future = asyncio.Future()
        request = HTTPRequest(TestSQLExporterClass.url)
        response = HTTPResponse(
            request, 200, None, io.BytesIO(b'{"data": true}')
        )
        future.set_result(response)
        mocker.patch(TestSQLExporterClass.function, return_value=future)

    @staticmethod
    @pytest.fixture(scope="function")
    def async_http_response_not_ok(mocker):
        """
        Patch fetch function to raise HTTPClientError.
        """

        def _side_effect(*args, **kwargs):
            raise HTTPClientError(509, "Timeout", None)

        future = asyncio.Future()
        future.set_result(_side_effect)
        mocker.patch(TestSQLExporterClass.function, side_effect=_side_effect)

    def test_not_allowed(self):
        """
        Given: Value of url is not contained in allowed collection and
        observation is initialized
        When: Accessing allowed property
        Expected: Returns False
        """
        observation = HTTPObservation(
            "https://notexample.com", allowed=(self.url,), callback=int
        )
        assert not observation.allowed

    def test_allowed(self):
        """
        Given: Value of url is contained in allowed collection and
        observation is initialized
        When: Accessing allowed property
        Expected: Returns True
        """
        observation = HTTPObservation(
            self.url, allowed=(self.url,), callback=int
        )
        assert observation.allowed

    @pytest.mark.asyncio
    @pytest.mark.xfail(raises=BasicObservationException)
    async def test_observe_callback_unsuccessfully(
        self, async_http_response_ok
    ):
        """
        Given: Observation is initialized with faulty callback function
        When: Instance calls observe function
        Expected: BasicObservationException is raised
        """
        with pytest.raises(BasicObservationException):
            observation = HTTPObservation(
                self.url, allowed=(self.url,), callback=int
            )
            await observation.observe()

    @pytest.mark.asyncio
    async def test_observe_callback_successfully(self, async_http_response_ok):
        """
        Given: Observation is initialized with proper callback function
        When: Instance calls observe function
        Expected: Callback returns object without exception raised
        """

        def callback(response):
            return json.loads(response.body)

        observation = HTTPObservation(
            self.url, allowed=(self.url,), callback=callback
        )
        result = await observation.observe()
        assert result["data"]

    @pytest.mark.asyncio
    async def test_observe_fetch_unsuccessfully(
        self, async_http_response_not_ok
    ):
        """
        Given: Observation is initialized with proper callback function
        When: Instance calls observe function but HTTPClientError is raised
        Expected: Function observe returns None
        """

        def callback(response):
            return json.loads(response.body)

        observation = HTTPObservation(
            self.url, allowed=(self.url,), callback=callback
        )
        result = await observation.observe()
        assert not result
