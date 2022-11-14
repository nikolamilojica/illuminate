class IAssistant:
    """Interface for Assistant class."""

    @staticmethod
    def create_alembic_config(path, url):
        """Creates Alembic's configuration object."""
        raise NotImplementedError

    @staticmethod
    def create_db_url(selector, settings):
        """Creates database URL."""
        raise NotImplementedError

    @staticmethod
    def import_settings():
        """Imports project's settings.py module and returns it."""
        raise NotImplementedError

    @staticmethod
    def provide_context(_filter):
        """Creates Manager's constructor kwargs."""
        raise NotImplementedError
