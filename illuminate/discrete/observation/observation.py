class Interface:
    """Interface for Observation class"""
    async def observe(self, *args, **kwargs):
        """Read source and use observer's callback function against response"""
        raise NotImplementedError
