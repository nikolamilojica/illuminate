class IObserver:
    """Interface for Observer class"""

    async def observe(self, response, *args, **kwargs):
        """Extract observations and/or findings from response"""
        raise NotImplementedError
