class IExporter:
    """Interface for Exporter class."""

    async def export(self, *args, **kwargs):
        """Writes data to destination."""
        raise NotImplementedError
