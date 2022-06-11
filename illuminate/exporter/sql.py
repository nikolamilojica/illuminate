from illuminate.exceptions.manager import BasicManagerException
from illuminate.exporter.exporter import Exporter


class SQLExporter(Exporter):
    """SQLExporter class, responsible for writing to destination"""

    async def export(self, *args, **kwargs):
        """Load to destination"""
        raise BasicManagerException
