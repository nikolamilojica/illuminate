class IObservation:
    """Interface for Observation class."""

    async def observe(self, *args, **kwargs):
        """Reads data from the source."""
        raise NotImplementedError
