import pytest

from illuminate.exceptions.manager import BasicManagerException
from illuminate.manager.assistant import Assistant
from illuminate.manager.manager import Manager
from tests.shared.unit import Test


class TestAssistantClass(Test):
    def test_create_alembic_config_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.create_alembic_config
        Expected: Returns config instance
        """
        with self.path() as path:
            name = "example"
            Manager.project_setup(name, ".")
            settings = Assistant.import_settings()
            url = Assistant.create_db_url("main", settings)
            config = Assistant.create_alembic_config(path, url)
            assert config.get_main_option("sqlalchemy.url") == url

    def test_create_db_url_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.create_db_url
        Expected: Returns database URL
        """
        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            settings = Assistant.import_settings()
            url = Assistant.create_db_url("main", settings)
            assert url == "postgresql://illuminate:password@localhost/example"

    def test_create_async_db_url_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.create_db_url with _async=True option
        Expected: Returns async database URL
        """
        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            settings = Assistant.import_settings()
            url = Assistant.create_db_url("main", settings, _async=True)
            assert (
                url
                == "postgresql+asyncpg://illuminate:password@localhost/example"
            )

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_import_settings_unsuccessfully(self):
        """
        Given: Current directory is a not project directory
        When: Calling Assistant.import_settings
        Expected: BasicManagerException is raised
        """
        with pytest.raises(BasicManagerException):
            with self.path():
                Assistant.import_settings()

    def test_import_settings_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.import_settings
        Expected: Returns module
        """
        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            settings = Assistant.import_settings()
            assert settings.NAME == name

    def test_provide_context_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.provide_context
        Expected: Returns context dict
        """
        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            context = Assistant.provide_context()
            assert type(context) == dict
            assert len(context["adapters"]) == 1
            assert len(context["observers"]) == 1
            assert context["name"] == name

    def test_provide_sessions_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.provide_sessions
        Expected: Returns sessions dict
        """
        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            assert Assistant.provide_sessions()["postgresql"]
