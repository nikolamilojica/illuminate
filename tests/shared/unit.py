import os
import sys
import tempfile
from contextlib import contextmanager

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Test:
    """
    Test class with path context manager that provides tests with temporary
    directory placed on PYTHONPATH with sqlite database attached
    """

    db = "test"
    folder = None
    protocol = "sqlite://"

    @staticmethod
    def assert_project_structure(name, files, path, cwd=False):
        """
        Assert project structure
        :param name: str
        :param files: dir
        :param path: str
        :param cwd: bool
        :return: None
        """
        project_path = os.path.join(path, name) if not cwd else path
        assert os.path.exists(project_path)
        for _name, content in files.items():
            test_file_path = os.path.join(project_path, _name)
            assert os.path.exists(test_file_path)
            with open(test_file_path, "r") as file:
                assert content.format(name=name).strip() == file.read().strip()

    @property
    def engine(self):
        """
        Creates database engine
        :return: sqlalchemy.engine.Engine or None
        """
        _engine = create_engine(self.url) if self.url else None
        return _engine

    @contextmanager
    def path(self):
        """
        Put temporary directory path to PYTHONPATH, set it as cwd and clean imports
        :yields: _GeneratorContextManager, TemporaryDirectory
        """

        logger.remove()
        logger.add(sys.stdout, level="DEBUG")

        with tempfile.TemporaryDirectory() as path:
            sys.path.append(path)
            os.chdir(path)
            self.folder = path
            try:
                yield path
            finally:
                sys.path.remove(path)
                self.folder = None
                for module in sys.modules.copy():
                    try:
                        if sys.modules[module].__file__.startswith(path):
                            del sys.modules[module]
                    except AttributeError:
                        pass

    @property
    def session(self):
        """
        Create database session
        :return: sqlalchemy.orm.Session or None
        """
        _session = sessionmaker(self.engine)()
        return _session if self.engine else None

    @property
    def url(self):
        """
        Create database URL
        :return: str or None
        """
        _url = (
            f"{self.protocol}/{self.folder}/{self.db}.db"
            if self.folder
            else None
        )
        return _url
