from illuminate.exceptions.observation import BasicObservationException
from illuminate.interface.observation import IObservation


class Observation(IObservation):
    """Observation class, responsible for reading source with callback"""

    async def observe(self, *args, **kwargs):
        """Read source and use observer's callback function against response"""
        raise BasicObservationException
