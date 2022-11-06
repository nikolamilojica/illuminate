from illuminate.exceptions.adapter import BasicAdapterException
from illuminate.interface.adapter import IAdapter


class Adapter(IAdapter):
    """Adapter class, responsible for producing exporters"""

    priority = None
    subscribers = None

    async def adapt(self, finding, *args, **kwargs):
        """Transform finding and produce exporters"""
        raise BasicAdapterException(
            "Method adapt must be implemented in child class"
        )
