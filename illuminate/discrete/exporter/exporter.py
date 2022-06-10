class Interface(object):
    """Interface for exporter class"""
    async def export(self, item, *args, **kwargs):
        """Perform load upon item"""
        return NotImplemented
