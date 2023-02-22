import pytest

from illuminate.manager import Manager
from illuminate.observation import FileObservation
from tests.unit import Test


async def _observe(_file):
    async for line in _file:
        yield line.strip()


class TestSQLObservationClass(Test):
    def test_observation_hash(self):
        """
        Given: FileObservations are initialized with different URLs
        When: Comparing hash values of FileObservation objects
        Expected: They are not the same
        """

        observation_1 = FileObservation("/root/data1.csv", _observe)
        observation_2 = FileObservation("/root/data2.csv", _observe)
        assert hash(observation_1) != hash(observation_2)

    @pytest.mark.asyncio
    async def test_observe_successfully(self):
        """
        Given: FileObservation is initialized with proper callback function and
        URL
        When: Instance calls observe function
        Expected: Callback returns object without exception raised
        """

        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            observation = FileObservation("models/__init__.py", _observe)
            content = []
            async with observation.observe() as results:
                async for r in results:
                    content.append(r)
            assert len(content) == 3
            assert content[0] == "from sqlalchemy.orm import declarative_base"
            assert content[2] == "Base = declarative_base()"

    @pytest.mark.asyncio
    async def test_observe_unsuccessfully(self):
        """
        Given: FileObservation is initialized with none existing URL
        When: Instance calls observe function
        Expected: Function observe returns None
        """

        observation = FileObservation("non-existing.csv", _observe)
        async with observation.observe() as results:
            assert not results
