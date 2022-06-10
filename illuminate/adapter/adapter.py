from illuminate.discrete.adapter.adapter import Interface
from illuminate.exceptions.manager import BasicManagerException


class Adapter(Interface):
    """Interface for adapter class"""
    def adapt(self, item, *args, **kwargs):
        """Perform transformation upon item"""
        raise BasicManagerException
