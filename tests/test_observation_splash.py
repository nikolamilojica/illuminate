import json

import pytest

from illuminate import __version__
from illuminate.observation import SplashObservation


class TestSplashObservationClass:

    http = {
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
    splash_html = {
        "body": "",
        "headers": "",
        "host": "localhost",
        "method": "GET",
        "port": 8050,
        "protocol": "http",
        "render": "html",
        "timeout": 30,
    }
    splash_png = {
        "body": "",
        "headers": "",
        "host": "localhost",
        "method": "GET",
        "port": 8050,
        "protocol": "http",
        "render": "png",
        "timeout": 30,
    }
    url = "https://example.com"

    def test_hash_implementation_with_same_configuration(self):
        """
        Given: SplashObservation are initialized with different URLs and
        using the same configuration dict
        When: Comparing hash values of SplashObservation objects
        Expected: They are not the same
        """
        observation_1 = SplashObservation(
            "https://example.com/api/v1",
            allowed=(self.url,),
            callback=int,
            **self.splash_html,
        )
        observation_2 = SplashObservation(
            "https://example.com/api/v2",
            allowed=(self.url,),
            callback=int,
            **self.splash_html,
        )
        assert hash(observation_1) != hash(observation_2)

    def test_hash_implementation_with_same_url(self):
        """
        Given: SplashObservation are initialized with same URLs and
        using the different configuration dict
        When: Comparing hash values of HTTPObservation objects
        Expected: They are not the same
        """
        observation_1 = SplashObservation(
            "https://example.com/api/v1",
            allowed=(self.url,),
            callback=int,
            **self.splash_html,
        )

        observation_2 = SplashObservation(
            "https://example.com/api/v1",
            allowed=(self.url,),
            callback=int,
            **self.splash_png,
        )
        assert hash(observation_1) != hash(observation_2)

    def test_not_allowed(self):
        """
        Given: Value of url is not contained in allowed collection and
        SplashObservation is initialized
        When: Accessing allowed property
        Expected: Returns False
        """
        observation = SplashObservation(
            "https://notexample.com", allowed=(self.url,), callback=int
        )
        assert not observation.allowed

    def test_allowed(self):
        """
        Given: Value of url is contained in allowed collection and
        SplashObservation is initialized
        When: Accessing allowed property
        Expected: Returns True
        """
        observation = SplashObservation(
            self.url, allowed=(self.url,), callback=int
        )
        assert observation.allowed

    @pytest.mark.asyncio
    async def test_observe_callback_unsuccessfully(
        self, async_http_response_ok
    ):
        """
        Given: SplashObservation is initialized with faulty callback function
        When: Instance calls observe function
        Expected: BasicObservationException is raised
        """
        observation = SplashObservation(
            self.url, allowed=(self.url,), callback=int, **self.splash_html
        )
        result = await observation.observe(self.http)
        assert not result

    @pytest.mark.asyncio
    async def test_observe_callback_successfully(self, async_http_response_ok):
        """
        Given: SplashObservation is initialized with proper callback function
        When: Instance calls observe function
        Expected: Callback returns object without exception raised
        """

        def callback(response):
            return json.loads(response.body)

        observation = SplashObservation(
            self.url,
            allowed=(self.url,),
            callback=callback,
            **self.splash_html,
        )
        result = await observation.observe(self.http)
        assert result["data"]

    @pytest.mark.asyncio
    async def test_observe_fetch_unsuccessfully(
        self, async_http_response_not_ok
    ):
        """
        Given: SplashObservation is initialized with proper callback function
        When: Instance calls observe function but HTTPClientError is raised
        Expected: Function observe returns None
        """

        def callback(response):
            return json.loads(response.body)

        observation = SplashObservation(
            self.url, allowed=(self.url,), callback=callback
        )
        result = await observation.observe(self.http)
        assert not result
