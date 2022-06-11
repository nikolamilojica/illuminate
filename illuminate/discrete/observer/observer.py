class Interface(object):
    """Interface for observer class"""
    async def observe(self, *args, **kwargs):
        """Extract observations or resume observing"""
        return NotImplemented
