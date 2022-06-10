from illuminate.discrete.exporter.exporter import Interface
from illuminate.exceptions.manager import BasicManagerException


class Exporter(Interface):

    def export(self, item, *args, **kwargs):
        """Perform load upon item"""
        raise BasicManagerException
