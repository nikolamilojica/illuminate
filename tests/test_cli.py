import pytest
from click.testing import CliRunner

from illuminate import __version__
from illuminate.cli import cli
from illuminate.manager import Manager
from tests.exception import TestANSIException
from tests.unit import Test


class TestCLI(Test):

    function = "tornado.httpclient.AsyncHTTPClient.fetch"
    influxdb_url = "influxdb://son:son@localhost/example"

    @staticmethod
    @pytest.fixture(scope="function")
    def raise_exception_with_ansi_tag_look_alike_message(mocker):
        """
        Patch fetch function to raise TestANSIException.
        """
        mocker.patch(TestCLI.function, side_effect=TestANSIException())

    def test_manage_project_setup_unsuccessfully(self):
        """
        Given: There is already a folder with same name
        When: Running 'illuminate manage project setup <name> <path>'
        Expected: Project is not created
        """
        with self.path() as path:
            name = "example"
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path) as tmp:
                Manager.project_setup(name, tmp)
                result = runner.invoke(
                    cli, ["manage", "project", "setup", name, tmp]
                )
                assert not result.output

    def test_manage_project_setup_successfully(self):
        """
        Given: There is no folder with same name
        When: Running 'illuminate manage project setup <name> <path>'
        Expected: Project is created
        """
        with self.path() as path:
            name = "example"
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path):
                result = runner.invoke(
                    cli, ["manage", "project", "setup", name, "."]
                )
                assert "Project structure created" in result.output

    def test_manage_db_revision_exception(self):
        """
        Given: Current directory is a project directory
        When: Running 'illuminate manage db revision' referencing wrong
        database type with selector option
        Expected: BasicManagerException is raised
        """
        with self.path() as path:
            name = "example"
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path) as tmp:
                runner.invoke(cli, ["manage", "project", "setup", name, "."])
                result = runner.invoke(
                    cli,
                    [
                        "manage",
                        "db",
                        "revision",
                        "--selector",
                        "measurements",
                        tmp,
                    ],
                )
                assert (
                    "Command revision can only be performed on SQL "
                    "database, measurements is not supported SQL database"
                ) in result.exception.__str__()

    def test_manage_db_revision_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Running 'illuminate manage db revision'
        Expected: Revision is not created
        """
        with self.path() as path:
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path):
                result = runner.invoke(cli, ["manage", "db", "revision"])
                assert not result.output

    def test_manage_db_revision_successfully(self):
        """
        Given: Current directory is a project directory
        When: Running 'illuminate manage db revision'
        Expected: Revision is created
        """
        with self.path() as path:
            name = "example"
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path) as tmp:
                runner.invoke(cli, ["manage", "project", "setup", name, "."])
                result = runner.invoke(
                    cli, ["manage", "db", "revision", "--url", self.url, tmp]
                )
                assert "Revision created" in result.output

    def test_manage_db_upgrade_exception(self):
        """
        Given: Current directory is a project directory
        When: Running 'illuminate manage db upgrade' referencing wrong
        database type with selector option
        Expected: BasicManagerException is raised
        """
        with self.path() as path:
            name = "example"
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path) as tmp:
                runner.invoke(cli, ["manage", "project", "setup", name, "."])
                runner.invoke(
                    cli, ["manage", "db", "revision", "--url", self.url, tmp]
                )
                result = runner.invoke(
                    cli,
                    [
                        "manage",
                        "db",
                        "upgrade",
                        "--selector",
                        "measurements",
                        tmp,
                    ],
                )
                assert (
                    "Command upgrade can only be performed on SQL "
                    "database, measurements is not supported SQL database"
                ) in result.exception.__str__()

    def test_manage_db_upgrade_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Running 'illuminate manage db upgrade'
        Expected: Data base is not upgraded
        """
        with self.path() as path:
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path):
                result = runner.invoke(cli, ["manage", "db", "upgrade"])
                assert not result.output

    def test_manage_db_upgrade_successfully(self):
        """
        Given: Current directory is a project directory
        When: Running 'illuminate manage db upgrade'
        Expected: Data base is upgraded
        """
        with self.path() as path:
            name = "example"
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path) as tmp:
                runner.invoke(cli, ["manage", "project", "setup", name, "."])
                runner.invoke(
                    cli, ["manage", "db", "revision", "--url", self.url, tmp]
                )
                result = runner.invoke(
                    cli, ["manage", "db", "upgrade", "--url", self.url, tmp]
                )
                assert "Database main upgraded" in result.output

    def test_manage_db_populate_exception(self):
        """
        Given: Current directory is a project directory
        When: Running 'illuminate manage db populate' referencing wrong
        database type with selector option
        Expected: BasicManagerException is raised
        """
        with self.path() as path:
            name = "example"
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path) as tmp:
                runner.invoke(cli, ["manage", "project", "setup", name, "."])
                runner.invoke(
                    cli, ["manage", "db", "revision", "--url", self.url, tmp]
                )
                runner.invoke(
                    cli, ["manage", "db", "upgrade", "--url", self.url, tmp]
                )
                result = runner.invoke(
                    cli,
                    [
                        "manage",
                        "db",
                        "populate",
                        "--selector",
                        "measurements",
                        "--fixtures",
                        f"{tmp}/fixtures/example.json",
                    ],
                )
                assert (
                    "Command populate can only be performed on SQL "
                    "database, measurements is not supported SQL database"
                ) in result.exception.__str__()

    def test_manage_db_populate_unsuccessfully(self):
        """
        Given: Current directory is a project directory
        When: Running 'illuminate manage db populate'
        Expected: Data base is not populated
        """
        with self.path() as path:
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path):
                result = runner.invoke(
                    cli,
                    [
                        "manage",
                        "db",
                        "populate",
                        "--fixtures",
                        f"{path}/fixtures/example.json",
                    ],
                )
                assert "example.json' does not exist" in result.output

    def test_manage_db_populate_successfully(self):
        """
        Given: Current directory is a project directory
        When: Running 'illuminate manage db populate'
        Expected: Data base is populated
        """
        with self.path() as path:
            name = "example"
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path) as tmp:
                runner.invoke(cli, ["manage", "project", "setup", name, "."])
                runner.invoke(
                    cli, ["manage", "db", "revision", "--url", self.url, tmp]
                )
                runner.invoke(
                    cli, ["manage", "db", "upgrade", "--url", self.url, tmp]
                )
                result = runner.invoke(
                    cli,
                    [
                        "manage",
                        "db",
                        "populate",
                        "--url",
                        self.url,
                        "--fixtures",
                        f"{tmp}/fixtures/example.json",
                    ],
                )
                assert "Database main populated" in result.output

    def test_observe_catalogue_label_successfully(self):
        """
        Given: Current directory is a project directory
        When: Running 'illuminate observe catalogue --label none=existing'
        Expected: BasicManagerException is raised since all Observers are
        filtered out.
        """
        with self.path() as path:
            name = "example"
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path):
                runner.invoke(cli, ["manage", "project", "setup", name, "."])
                result = runner.invoke(
                    cli, ["observe", "catalogue", "--label", "none=existing"]
                )
                assert (
                    result.exception.__str__()
                    == "No observers found or left after filtering"
                )

    def test_observe_catalogue_unsuccessfully(self):
        """
        Given: Current directory is not a project directory
        When: Running 'illuminate observe catalogue'
        Expected: Observer list is not presented
        """
        with self.path() as path:
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path):
                result = runner.invoke(cli, ["observe", "catalogue"])
                assert not result.output

    def test_observe_catalogue_successfully(self):
        """
        Given: Current directory is a project directory
        When: Running 'illuminate observe catalogue'
        Expected: Observer list is presented
        """
        with self.path() as path:
            name = "example"
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path):
                runner.invoke(cli, ["manage", "project", "setup", name, "."])
                result = runner.invoke(cli, ["observe", "catalogue"])
                assert (
                    "<class 'observers.example.ObserverExample'>"
                    in result.output
                )
                assert (
                    "[('https://webscraper.io/', 'observe')]" in result.output
                )

    def test_observe_start_label_successfully(
        self, raise_exception_with_ansi_tag_look_alike_message
    ):
        """
        Given: Current directory is a project directory
        When: Running 'illuminate observe start --label none=existent'
        Expected: BasicManagerException is raised since all Observers are
        filtered out.
        """
        with self.path() as path:
            name = "example"
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path) as tmp:
                runner.invoke(cli, ["manage", "project", "setup", name, "."])
                runner.invoke(
                    cli, ["manage", "db", "revision", "--url", self.url, tmp]
                )
                runner.invoke(
                    cli, ["manage", "db", "upgrade", "--url", self.url, tmp]
                )
                runner.invoke(
                    cli, ["manage", "db", "upgrade", "--url", self.url, tmp]
                )
                result = runner.invoke(
                    cli, ["observe", "start", "--label", "none=existing"]
                )
                assert (
                    result.exception.__str__()
                    == "No observers found or left after filtering"
                )

    def test_observe_start_not_blocking_with_ansi_quasi_tag_exc_successfully(
        self, raise_exception_with_ansi_tag_look_alike_message
    ):
        """
        Given: Current directory is a project directory
        When: Running 'illuminate observe start' with forced exception that
        has a message with quasi ANSI tag message
        Expected: Async loop is not broken and the process comes to an end with
        a message displayed after escaping quasi ANSI tags
        """
        with self.path() as path:
            name = "example"
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path) as tmp:
                runner.invoke(cli, ["manage", "project", "setup", name, "."])
                runner.invoke(
                    cli, ["manage", "db", "revision", "--url", self.url, tmp]
                )
                runner.invoke(
                    cli, ["manage", "db", "upgrade", "--url", self.url, tmp]
                )
                runner.invoke(
                    cli, ["manage", "db", "upgrade", "--url", self.url, tmp]
                )
                result = runner.invoke(cli, ["observe", "start"])
                assert "\n<string>\n" in result.output

    def test_version(self):
        """
        Given: None
        When: Running 'illuminate --version'
        Expected: Version is shown
        """
        with self.path() as path:
            runner = CliRunner()
            with runner.isolated_filesystem(temp_dir=path):
                result = runner.invoke(cli, ["--version"])
                assert __version__ in result.output
