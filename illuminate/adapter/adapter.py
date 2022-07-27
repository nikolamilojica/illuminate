from illuminate.discrete.adapter.adapter import Interface
from illuminate.exceptions.manager import BasicManagerException


class Adapter(Interface):
    """Adapter class, responsible for producing exporters"""

    async def adapt(self, finding, *args, **kwargs):
        """Transform finding and produce exporters"""
        raise BasicManagerException
