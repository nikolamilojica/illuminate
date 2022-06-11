class Interface(object):
    """Interface for exporter class"""
    async def export(self, item, *args, **kwargs):
        """Load transformation to destination"""
        return NotImplemented
