from click.testing import CliRunner

from illuminate import __version__
from illuminate.cli import cli
from illuminate.manager import Manager
from tests.unit import Test


class TestCLI(Test):

    influxdb_url = "influxdb://son:son@localhost/example"

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
                    ["manage", "db", "populate", "--selector", "measurements"],
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
                result = runner.invoke(cli, ["manage", "db", "populate"])
                assert not result.output

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
                    cli, ["manage", "db", "populate", "--url", self.url]
                )
                assert "Database main populated" in result.output

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
                    "<class 'observers.example.py.ObserverExample'>"
                    in result.output
                )
                assert (
                    "[('https://webscraper.io/', 'observe')]" in result.output
                )

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
