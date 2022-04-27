class Interface(object):
    """Interface for manager class"""

    @classmethod
    def setup(cls, name, path):
        """Create project directory and populates it with project files"""
        raise NotImplementedError
