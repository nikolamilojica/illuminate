class Interface:
    """Interface for Assistant class"""

    @staticmethod
    def create_alembic_config(path, url):
        """Creates config object needed to perform Alembic commands"""
        raise NotImplementedError

    @staticmethod
    def create_db_url(selector, settings):
        """Creates db url from data in settings.py module"""
        raise NotImplementedError

    @staticmethod
    def import_settings():
        """Tries to import project settings.py module and returns it"""
        raise NotImplementedError

    @staticmethod
    def provide_context():
        """Provides context for the current runtime"""
        raise NotImplementedError
