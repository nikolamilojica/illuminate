from illuminate.exceptions.manager import BasicManagerException
from illuminate.interface.observer import Interface


class Observer(Interface):
    """Observer class, responsible for producing observations and findings"""

    def __init__(self):
        self.initial_observations = []

    async def observe(self, response, *args, **kwargs):
        """Extract observations and/or findings from response"""
        raise BasicManagerException
