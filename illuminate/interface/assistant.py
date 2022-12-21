class IAssistant:
    """Interface for Assistant class."""

    @staticmethod
    def provide_alembic_config(path, selector, url):
        """Creates Alembic's configuration object."""
        raise NotImplementedError

    @staticmethod
    def provide_alembic_operations(selector, url):
        """Creates Alembic's operations object."""
        raise NotImplementedError

    @staticmethod
    def provide_context(sessions, _filter):
        """Creates Manager's constructor kwargs."""
        raise NotImplementedError

    @staticmethod
    def provide_models():
        """Gathers project models."""
        raise NotImplementedError

    @staticmethod
    def _provide_db_url(selector):
        """Creates database URL."""
        raise NotImplementedError

    @staticmethod
    def _provide_sessions():
        """Creates a dictionary of database sessions."""
        raise NotImplementedError

    @staticmethod
    def _provide_settings():
        """Imports project's settings.py module and returns it."""
        raise NotImplementedError
