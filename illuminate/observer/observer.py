from illuminate.discrete.observer.observer import Interface
from illuminate.exceptions.manager import BasicManagerException


class Observer(Interface):

    def __init__(self):
        self.initial_observations = []

    def start(self, response, *args, **kwargs):
        """ETL entry point after initial observation"""
        raise BasicManagerException
