class IManager:
    """Interface for Manager class"""

    @staticmethod
    def db_populate(fixtures, selector, url=None):
        """Populates db with Alembic framework"""
        raise NotImplementedError

    @staticmethod
    def db_revision(path, revision, selector, url=None, *args, **kwargs):
        """Creates db revision with Alembic framework"""
        raise NotImplementedError

    @staticmethod
    def db_upgrade(path, revision, selector, url=None):
        """Performs db migration with Alembic framework"""
        raise NotImplementedError

    @staticmethod
    def project_setup(name, path):
        """Create project directory and populates it with project files"""
        raise NotImplementedError

    def observe_start(self):
        """Start producer/consumer ETL process based on project files"""
        raise NotImplementedError
