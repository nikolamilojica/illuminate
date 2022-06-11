from illuminate.discrete.adapter.adapter import Interface
from illuminate.exceptions.manager import BasicManagerException


class Adapter(Interface):

    async def adapt(self, item, *args, **kwargs):
        """Transform observation and produce exporters"""
        raise BasicManagerException
