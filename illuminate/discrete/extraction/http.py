class Interface(object):
    """Interface for HTTP extraction class"""
    async def callback(self, *args, **kwargs):
        return NotImplemented
