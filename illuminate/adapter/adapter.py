from illuminate.discrete.adapter.adapter import Interface
from illuminate.exceptions.manager import BasicManagerException


class Adapter(Interface):

    def adapt(self, item, *args, **kwargs):
        """Perform transformation upon item"""
        raise BasicManagerException
