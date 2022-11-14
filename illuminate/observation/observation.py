from illuminate.exceptions.observation import BasicObservationException
from illuminate.interface.observation import IObservation


class Observation(IObservation):
    """
    Observation class, reads data from the source. Class must be inherited and
    method observe must be implemented in a child class.
    """

    async def observe(self, *args, **kwargs):
        """
        Reads data from the source. Must be implemented in a child class.

        :return: None
        :raises BasicObservationException:
        """
        raise BasicObservationException(
            "Method observe must be implemented in child class"
        )
