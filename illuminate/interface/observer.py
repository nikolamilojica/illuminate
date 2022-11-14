class IObserver:
    """Interface for Observer class."""

    async def observe(self, response, *args, **kwargs):
        """
        Manipulates response object and yields Exporter, Finding and
        Observation objects.
        """
        raise NotImplementedError
