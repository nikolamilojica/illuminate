from illuminate.discrete.observer.observer import Interface
from illuminate.exceptions.manager import BasicManagerException


class Observer(Interface):

    def __init__(self):
        self.initial_observations = []

    async def observe(self, response, *args, **kwargs):
        """Extract observations or resume observing"""
        raise BasicManagerException
