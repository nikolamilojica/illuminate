class Interface:
    """Interface for Exporter class"""
    async def export(self, item, *args, **kwargs):
        """Load to destination"""
        return NotImplemented
