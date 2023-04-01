import os

import pytest
from sqlalchemy.sql import text

from illuminate.manager import Manager
from illuminate.observation import SQLObservation
from tests.unit import Test


async def callback_with_assert(results):
    i = 0
    _results = results.fetchall()
    assert len(_results) == 2
    for r in _results:
        i += 1
        if i == 0:
            assert r.title == "Web Scraper Tutorials"
            assert r.url == "https://webscraper.io/tutorials"
        if i == 1:
            assert r.title == "Web Scraper - The #1 web scraping extension"
            assert r.url == "https://webscraper.io/"
        yield r


class TestSQLObservationClass(Test):

    query = text("SELECT * FROM example")

    def test_observation_hash(self):
        """
        Given: SQLObservations are initialized with different URLs and
        using the same query object
        When: Comparing hash values of SQLObservation objects
        Expected: They are not the same
        """

        observation_1 = SQLObservation(
            self.query, "main", callback_with_assert
        )
        observation_2 = SQLObservation(
            self.query, "backup", callback_with_assert
        )
        assert hash(observation_1) != hash(observation_2)

    @pytest.mark.asyncio
    async def test_observe_successfully(self):
        """
        Given: SQLObservation is initialized with proper callback function
        When: Instance calls observe function
        Expected: Callback returns object without exception raised
        """

        with self.path() as path:
            name = "example"
            Manager.project_setup(name, ".")
            Manager.db_revision(path, "head", "main", self.url)
            Manager.db_upgrade(path, "head", "main", self.url)
            Manager.db_populate(["fixtures/example.json"], "main", self.url)
            observation = SQLObservation(
                self.query, "main", callback_with_assert
            )
            results = await observation.observe(self.session_async)
            async for r in results:
                _ = r

    @pytest.mark.asyncio
    async def test_observe_unsuccessfully(self):
        """
        Given: SQLObservation is initialized with proper callback function
        When: Instance calls observe function but SQLAlchemyError is raised
        Expected: Function observe returns None
        """

        with self.path() as path:
            name = "example"
            Manager.project_setup(name, ".")
            Manager.db_revision(path, "head", "main", self.url)
            Manager.db_upgrade(path, "head", "main", self.url)
            Manager.db_populate(["fixtures/example.json"], "main", self.url)
            observation = SQLObservation(
                self.query, "main", callback_with_assert
            )
            os.remove(os.path.join(path, f"{self.db}.db"))
            results = await observation.observe(self.session_async)
            assert not results
