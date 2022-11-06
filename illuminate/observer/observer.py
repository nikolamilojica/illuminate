from illuminate.exceptions.observer import BasicObserverException
from illuminate.interface.observer import IObserver


class Observer(IObserver):
    """Observer class, responsible for producing observations and findings"""

    def __init__(self):
        self.initial_observations = []

    async def observe(self, response, *args, **kwargs):
        """Extract observations and/or findings from response"""
        raise BasicObserverException(
            "Method observe must be implemented in child class"
        )
