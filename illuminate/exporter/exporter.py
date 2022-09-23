from illuminate.exceptions.exporter import BasicExporterException
from illuminate.interface.exporter import IExporter


class Exporter(IExporter):
    """Exporter class, responsible for writing to destination"""

    async def export(self, *args, **kwargs):
        """Load to destination"""
        raise BasicExporterException
