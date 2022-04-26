class Interface(object):
    """Interface for manager class"""
    def __init__(self, name, path):
        raise NotImplementedError

    def create_project(self):
        """Create project directory and populates it with needed files"""
        raise NotImplementedError
