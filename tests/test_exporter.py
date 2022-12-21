import pytest

from illuminate.exceptions.exporter import BasicExporterException
from illuminate.exporter.exporter import Exporter


class TestExporter:
    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    @pytest.mark.xfail(raises=BasicExporterException)
    def test_not_implemented_export(self):
        """
        Given: Exporter class is not inherited and instantiated
        When: calling export method
        Expected: BasicExporterException is raised
        """
        exporter = Exporter()
        exporter.export()
