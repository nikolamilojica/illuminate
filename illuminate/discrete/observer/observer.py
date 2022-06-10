class Interface(object):
    """Interface for observer class"""
    async def observe(self, *args, **kwargs):
        """Extract instances of observation class or reschedule extraction"""
        return NotImplemented
