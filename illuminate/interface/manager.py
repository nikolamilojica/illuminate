class IManager:
    """Interface for Manager class."""

    @staticmethod
    def db_populate(fixtures, models, operations, selector):
        """Populates database with fixtures."""
        raise NotImplementedError

    @staticmethod
    def db_revision(config, revision):
        """Creates Alembic's revision file in migration directory."""
        raise NotImplementedError

    @staticmethod
    def db_upgrade(config, revision, selector):
        """Applies migration file to a database."""
        raise NotImplementedError

    @staticmethod
    def project_setup(name, path):
        """Creates a project directory with all needed files."""
        raise NotImplementedError

    def observe_start(self):
        """Starts producer/consumer ETL process."""
        raise NotImplementedError
