class Interface(object):
    """Interface for adapter class"""
    async def adapt(self, item, *args, **kwargs):
        """Perform transformation upon item"""
        return NotImplemented
