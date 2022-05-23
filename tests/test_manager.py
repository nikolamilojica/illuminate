import os
import tempfile

import pytest

from illuminate.common.project_templates import FILES
from illuminate.exceptions.manager import BasicManagerException
from illuminate.manager.manager import Manager


class TestManagerClassInstance:
    def test_singleton_behaviour_successfully(self):
        """
        Given: None
        When: Creating instance of Manager class twice with different arguments
        Expected: Instances are the same
        """
        manager_1 = Manager("premier-league", "/opt/premier-league")
        manager_2 = Manager("bundesliga", "/opt/bundesliga")
        assert manager_1 == manager_2


class TestManagerProjectCommandGroup:
    @staticmethod
    def assert_project_structure(name, path, cwd=False):
        """
        Helper method for asserting project structure
        :param name: name of the project: str
        :param path: path of the project: str
        :param cwd: assert in same folder: bool
        :return: None
        """
        project_path = os.path.join(path, name) if not cwd else path
        assert os.path.exists(project_path)
        for _name, content in FILES.items():
            test_file_path = os.path.join(project_path, _name)
            assert os.path.exists(test_file_path)
            with open(test_file_path, "r") as file:
                assert content.format(name=name).strip() == file.read().strip()

    def test_setup_successfully(self):
        """
        Given: No directory or file exists with the same name as project
        When: Setting up new project
        Expected: Creates directories and files needed for framework
        """
        with tempfile.TemporaryDirectory() as path:
            name = "bundesliga"
            Manager.project_setup(name, path)
            self.assert_project_structure(name, path)

    def test_setup_in_current_folder_successfully(self):
        """
        Given: Current working directory is target for project files
        When: Setting up new project
        Expected: Creates directories and files needed for framework
        """
        with tempfile.TemporaryDirectory() as path:
            os.chdir(path)
            name = "bundesliga"
            Manager.project_setup(name, ".")
            self.assert_project_structure(name, path, cwd=True)

    @pytest.mark.xfail(raises=BasicManagerException)
    def test_setup_unsuccessfully_directory_or_file_exists(self):
        """
        Given: Directory of file exists with the same name as project
        When: Setting up new project
        Expected: Raise exception
        NOTE: This test will clean files from test_setup_successfully
        """
        with pytest.raises(BasicManagerException) as error:
            name = "bundesliga"
            with tempfile.TemporaryDirectory() as path:
                Manager.project_setup(name, path)
                Manager.project_setup(name, path)
