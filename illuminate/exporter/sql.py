from illuminate.discrete.exporter.sql import Interface
from illuminate.exceptions.manager import BasicManagerException


class SQLExporter(Interface):

    async def export(self, item, *args, **kwargs):
        """Load transformation to destination"""
        raise BasicManagerException
