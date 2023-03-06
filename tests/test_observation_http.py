import json

import pytest

from illuminate import __version__
from illuminate.observation import HTTPObservation


class TestHTTPObservationClass:

    url = "https//:example.com"

    def test_hash_implementation_with_same_configuration(self):
        """
        Given: HTTPObservations are initialized with different URLs and
        using the same configuration dict
        When: Comparing hash values of HTTPObservation objects
        Expected: They are not the same
        """
        config = {
            "auth_username": None,
            "auth_password": None,
            "connect_timeout": 10.0,
            "body": None,
            "headers": None,
            "method": "GET",
            "request_timeout": 10.0,
            "user_agent": f"Illuminate-bot/{__version__}",
            "validate_cert": False,
        }
        observation_1 = HTTPObservation(
            "https://example.com/api/v1",
            allowed=(self.url,),
            callback=int,
            **config,
        )
        observation_2 = HTTPObservation(
            "https://example.com/api/v2",
            allowed=(self.url,),
            callback=int,
            **config,
        )
        assert hash(observation_1) != hash(observation_2)

    def test_hash_implementation_with_same_url(self):
        """
        Given: HTTPObservations are initialized with same URLs and
        using the different configuration dict
        When: Comparing hash values of HTTPObservation objects
        Expected: They are not the same
        """
        config_1 = {
            "auth_username": None,
            "auth_password": None,
            "connect_timeout": 10.0,
            "body": {"measurement": "°C"},
            "headers": None,
            "method": "POST",
            "request_timeout": 10.0,
            "user_agent": f"Illuminate-bot/{__version__}",
            "validate_cert": False,
        }
        config_2 = {
            "auth_username": None,
            "auth_password": None,
            "connect_timeout": 10.0,
            "body": {"measurement": "K"},
            "headers": None,
            "method": "POST",
            "request_timeout": 10.0,
            "user_agent": f"Illuminate-bot/{__version__}",
            "validate_cert": False,
        }
        observation_1 = HTTPObservation(
            "https://example.com/api/v1",
            allowed=(self.url,),
            callback=int,
            **config_1,
        )
        observation_2 = HTTPObservation(
            "https://example.com/api/v1",
            allowed=(self.url,),
            callback=int,
            **config_2,
        )
        assert hash(observation_1) != hash(observation_2)

    def test_not_allowed(self):
        """
        Given: Value of url is not contained in allowed collection and
        HTTPObservations is initialized
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
        HTTPObservations is initialized
        When: Accessing allowed property
        Expected: Returns True
        """
        observation = HTTPObservation(
            self.url, allowed=(self.url,), callback=int
        )
        assert observation.allowed

    @pytest.mark.asyncio
    async def test_observe_callback_unsuccessfully(
        self, async_http_response_ok
    ):
        """
        Given: HTTPObservations is initialized with faulty callback function
        When: Instance calls observe function
        Expected: BasicObservationException is raised
        """
        observation = HTTPObservation(
            self.url, allowed=(self.url,), callback=int
        )
        result = await observation.observe()
        assert not result

    @pytest.mark.asyncio
    async def test_observe_callback_successfully(self, async_http_response_ok):
        """
        Given: HTTPObservations is initialized with proper callback function
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
        Given: HTTPObservations is initialized with proper callback function
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
