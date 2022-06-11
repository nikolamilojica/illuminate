from illuminate.exceptions.manager import BasicManagerException
from illuminate.exporter.exporter import Exporter


class SQLExporter(Exporter):

    async def export(self, item, *args, **kwargs):
        """Load transformation to destination"""
        raise BasicManagerException
