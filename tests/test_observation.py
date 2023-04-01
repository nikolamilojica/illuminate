import pytest

from illuminate.exceptions import BasicObservationException
from illuminate.observation import Observation


class TestObservation:
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    @pytest.mark.xfail(raises=BasicObservationException)
    def test_not_implemented_observe(self):
        """
        Given: Observation class is not inherited and instantiated
        When: calling observe method
        Expected: BasicObservationException is raised
        """
        observer = Observation("https://www.example.com")
        observer.observe()
