import pytest
from alembic.operations import Operations

from illuminate.exceptions import BasicManagerException
from illuminate.manager import Assistant
from illuminate.manager import Manager
from tests.unit import Test


class TestAssistantClass(Test):
    @pytest.mark.xfail(raises=BasicManagerException)
    def test_provide_alembic_config_unsuccessfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.provide_alembic_config with none defined
        database selector
        Expected: BasicManagerException is raised
        """
        with pytest.raises(BasicManagerException):
            with self.path() as path:
                name = "example"
                Manager.project_setup(name, ".")
                Assistant.provide_alembic_config(path, "backup")

    def test_provide_alembic_config_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.provide_alembic_config
        Expected: Returns config instance
        """
        with self.path() as path:
            name = "example"
            Manager.project_setup(name, ".")
            url = Assistant._provide_db_url("main")
            config = Assistant.provide_alembic_config(path, "main", url)
            assert config.get_main_option("sqlalchemy.url") == url

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_provide_alembic_operations_unsuccessfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.provide_alembic_operations with none defined
        database selector
        Expected: BasicManagerException is raised
        """
        with pytest.raises(BasicManagerException):
            with self.path():
                name = "example"
                Manager.project_setup(name, ".")
                assert isinstance(
                    Assistant.provide_alembic_operations("backup"),
                    Operations,
                )

    def test_provide_alembic_operations_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.provide_alembic_operations
        Expected: Returns Operations object
        """
        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            assert isinstance(
                Assistant.provide_alembic_operations("main", self.url),
                Operations,
            )

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_provide_context_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Calling Assistant.provide_context
        Expected: BasicManagerException is raised
        """
        with pytest.raises(BasicManagerException):
            Assistant.provide_context()

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
            assert context["sessions"]["main"]

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_provide_models_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Calling Assistant.provide_models
        Expected: BasicManagerException is raised
        """
        with pytest.raises(BasicManagerException):
            Assistant.provide_models()

    def test_provide_models_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.provide_models
        Expected: Returns list of models
        """
        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            assert Assistant.provide_models()[0]

    @pytest.mark.xfail(raises=BasicManagerException)
    def test__provide_db_url_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Calling Assistant._provide_db_url
        Expected: BasicManagerException is raised
        """
        with pytest.raises(BasicManagerException):
            Assistant._provide_db_url("main")

    @pytest.mark.xfail(raises=BasicManagerException)
    def test__provide_db_url_async_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Calling Assistant._provide_db_url
        Expected: BasicManagerException is raised
        """
        with pytest.raises(BasicManagerException):
            Assistant._provide_db_url("main", _async=True)

    def test__provide_db_url_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant._provide_db_url
        Expected: Returns database URL
        """
        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            url = Assistant._provide_db_url("main")
            assert url == "postgresql://illuminate:password@localhost/example"

    def test__provide_db_url_async_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant._provide_db_url with _async=True option
        Expected: Returns async database URL
        """
        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            url = Assistant._provide_db_url("main", _async=True)
            assert (
                url
                == "postgresql+asyncpg://illuminate:password@localhost/example"
            )

    def test__provide_sessions_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Calling Assistant._provide_sessions
        Expected: BasicManagerException is raised
        """
        with pytest.raises(BasicManagerException):
            Assistant._provide_sessions()

    def test__provide_sessions_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant._provide_sessions
        Expected: Returns sessions dict
        """
        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            assert Assistant._provide_sessions()["main"]

    @pytest.mark.xfail(raises=BasicManagerException)
    def test__provide_settings_unsuccessfully(self):
        """
        Given: Current directory is a not project directory
        When: Calling Assistant._provide_settings
        Expected: BasicManagerException is raised
        """
        with pytest.raises(BasicManagerException):
            with self.path():
                Assistant._provide_settings()

    def test__provide_settings_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant._provide_settings
        Expected: Returns module
        """
        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            settings = Assistant._provide_settings()
            assert settings.NAME == name
