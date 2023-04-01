import pytest

from illuminate.exceptions.observer import BasicObserverException
from illuminate.observer.observer import Observer


class TestObserver:
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    @pytest.mark.xfail(raises=BasicObserverException)
    def test_not_implemented_observe(self):
        """
        Given: Observer class is not inherited and instantiated
        When: calling observe method
        Expected: BasicObserverException is raised
        """
        observer = Observer()
        observer.observe(None)
