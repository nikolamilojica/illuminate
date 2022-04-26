class Interface(object):
    """Interface for manager class"""

    def create_project(self):
        """Create project directory and populates it with needed files"""
        raise NotImplementedError
