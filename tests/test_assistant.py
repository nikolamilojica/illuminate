import pytest
from alembic.operations import Operations

from illuminate.exceptions.manager import BasicManagerException
from illuminate.manager.assistant import Assistant
from illuminate.manager.manager import Manager
from tests.shared.unit import Test


class TestAssistantClass(Test):
    def test_provide_alembic_config_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.provide_alembic_config
        Expected: Returns config instance
        """
        with self.path() as path:
            name = "example"
            Manager.project_setup(name, ".")
            url = Assistant._create_db_url("main")
            config = Assistant.provide_alembic_config(path, "main", url)
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
            url = Assistant._create_db_url("main")
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
            url = Assistant._create_db_url("main", _async=True)
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
                Assistant._import_settings()

    def test_import_settings_successfully(self):
        """
        Given: Current directory is a project directory
        When: Calling Assistant.import_settings
        Expected: Returns module
        """
        with self.path():
            name = "example"
            Manager.project_setup(name, ".")
            settings = Assistant._import_settings()
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
            assert Assistant._provide_sessions()["postgresql"]

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
