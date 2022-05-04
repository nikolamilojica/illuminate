import os
import shutil

import pytest

from illuminate.common.project_templates import FILES
from illuminate.exceptions.manager import BasicManagerException
from illuminate.manager.manager import Manager


class TestManager:
    def test_singleton_behaviour_successfully(self):
        """
        Given: None
        When: Creating instance of Manager class twice with different arguments
        Expected: Instances are the same
        """
        manager_1 = Manager("premier-league", "/opt/premier-league")
        manager_2 = Manager("bundesliga", "/opt/bundesliga")
        assert manager_1 == manager_2


class TestManagerSetup:
    SETUP_NAME = "premier-league"
    SETUP_DIRECTORY = "/tmp"
    SETUP_DIRECTORY_PATH = os.path.join(SETUP_DIRECTORY, SETUP_NAME)

    @pytest.fixture
    def clean_files(self):
        yield
        shutil.rmtree(self.SETUP_DIRECTORY_PATH)

    @pytest.fixture(scope='session')
    def test_setup_successfully(self):
        """
        Given: No directory or file exists with the same name as project
        When: Setting up new project
        Expected: Creates directories and files needed for framework
        """
        Manager.setup(self.SETUP_NAME, self.SETUP_DIRECTORY)
        assert os.path.exists(self.SETUP_DIRECTORY_PATH)
        for name, content in FILES.items():
            test_file_path = os.path.join(self.SETUP_DIRECTORY_PATH, name)
            assert os.path.exists(test_file_path)
            with open(test_file_path, "r") as file:
                assert content.strip() == file.read().strip()

    @pytest.mark.usefixtures('test_setup_successfully')
    @pytest.mark.xfail(raises=BasicManagerException)
    def test_setup_unsuccessfully_directory_or_file_exists(self, clean_files):
        """
        Given: Directory of file exists with the same name as project
        When: Setting up new project
        Expected: Raise exception
        NOTE: This test will clean files from test_setup_successfully
        """
        with pytest.raises(BasicManagerException) as error:
            Manager.setup(self.SETUP_NAME, self.SETUP_DIRECTORY)
