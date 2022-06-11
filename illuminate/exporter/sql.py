from illuminate.discrete.exporter.sql import Interface
from illuminate.exceptions.manager import BasicManagerException


class SQLExporter(Interface):

    def export(self, item, *args, **kwargs):
        """Perform load upon item"""
        raise BasicManagerException
