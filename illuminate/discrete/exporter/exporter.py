class Interface:
    """Interface for Exporter class"""

    async def export(self, *args, **kwargs):
        """Load to destination"""
        raise NotImplementedError
