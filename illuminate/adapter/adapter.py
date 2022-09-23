from illuminate.exceptions.manager import BasicManagerException
from illuminate.interface.adapter import Interface


class Adapter(Interface):
    """Adapter class, responsible for producing exporters"""

    async def adapt(self, finding, *args, **kwargs):
        """Transform finding and produce exporters"""
        raise BasicManagerException
