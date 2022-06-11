class Interface:
    """Interface for Observer class"""
    async def observe(self, *args, **kwargs):
        """Extract observations and/or findings"""
        return NotImplemented
