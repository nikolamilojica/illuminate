import os

from alembic.config import Config

from illuminate.discrete.manager.assistant import Interface
from illuminate.exceptions.manager import BasicManagerException


class Assistant(Interface):
    @staticmethod
    def create_alembic_config(path, url):
        """Creates config object needed to perform Alembic commands"""
        config = Config()
        config.set_main_option("script_location", os.path.join(path, "migrations"))
        config.set_main_option("sqlalchemy.url", url)
        return config

    @staticmethod
    def create_db_url(selector, settings):
        """Creates db url from data in settings.py module"""
        db = settings.DB[selector]
        db["db"] = settings.NAME
        return "{type}://{user}:{pass}@{host}/{db}".format(**db)

    @staticmethod
    def import_settings():
        """Tries to import project settings.py module and returns it"""
        try:
            import settings

            return settings
        except ImportError:
            raise BasicManagerException
