from illuminate.discrete.observer.observer import Interface
from illuminate.exceptions.manager import BasicManagerException


class Observer(Interface):

    def __init__(self):
        self.initial_observations = []

    def observe(self, response, *args, **kwargs):
        """Extract instances of observation class or reschedule extraction"""
        raise BasicManagerException
