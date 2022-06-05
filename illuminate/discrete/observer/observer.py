class Interface(object):
    """Interface for observer class"""
    async def start(self, *args, **kwargs):
        """ETL entry point after initial observation"""
        return NotImplemented
