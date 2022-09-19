class Interface:
    """Interface for Adapter class"""
    async def adapt(self, finding, *args, **kwargs):
        """Transform finding and produce exporters"""
        raise NotImplementedError
