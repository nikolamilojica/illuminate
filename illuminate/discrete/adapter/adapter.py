class Interface(object):
    """Interface for adapter class"""
    async def adapt(self, item, *args, **kwargs):
        """Transform observation and produce exporters"""
        return NotImplemented
