class Interface(object):
    """Interface for observation class"""
    async def extract(self, *args, **kwargs):
        """Read source and use observer's callback function against response"""
        return NotImplemented
