class Interface:
    """Interface for Adapter class"""
    async def adapt(self, item, *args, **kwargs):
        """Transform finding and produce exporters"""
        return NotImplemented
