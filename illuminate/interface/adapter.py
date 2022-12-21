class IAdapter:
    """Interface for Adapter class."""

    async def adapt(self, finding, *args, **kwargs):
        """Generates Exporter and Observation objects."""
        raise NotImplementedError
