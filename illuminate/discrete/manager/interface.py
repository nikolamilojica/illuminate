class Interface(object):
    """Interface for manager class"""

    @classmethod
    def db(cls, action, path, revision, selector):
        """Creates/changes db schema with Alembic framework"""
        raise NotImplementedError

    @classmethod
    def setup(cls, name, path):
        """Create project directory and populates it with project files"""
        raise NotImplementedError