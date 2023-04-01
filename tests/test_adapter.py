import pytest

from illuminate.adapter import Adapter
from illuminate.exceptions import BasicAdapterException


class TestAdapter:
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    @pytest.mark.xfail(raises=BasicAdapterException)
    def test_not_implemented_adapt(self):
        """
        Given: Adapter class is not inherited and instantiated
        When: calling adapt method
        Expected: BasicAdapterException is raised
        """
        adapter = Adapter()
        adapter.adapt(None)
