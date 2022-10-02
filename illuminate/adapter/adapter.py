from illuminate.exceptions.adapter import BasicAdapterException
from illuminate.interface.adapter import IAdapter


class Adapter(IAdapter):
    """Adapter class, responsible for producing exporters"""

    async def adapt(self, finding, *args, **kwargs):
        """Transform finding and produce exporters"""
        raise BasicAdapterException
