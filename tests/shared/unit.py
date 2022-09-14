import os
import sys
import tempfile
from contextlib import contextmanager

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
        Puts temporary directory path to PYTHONPATH and use it as cwd
        :yields: _GeneratorContextManager, TemporaryDirectory
        """
        with tempfile.TemporaryDirectory() as path:
            sys.path.append(path)
            os.chdir(path)
            self.folder = path
            yield path
            sys.path.remove(path)
            self.folder = None

    @property
    def session(self):
        """
        Creates database session
        :return: sqlalchemy.orm.Session or None
        """
        _session = sessionmaker(self.engine)()
        return _session if self.engine else None

    @property
    def url(self):
        """
        Creates database URL
        :return: str or None
        """
        _url = f"{self.protocol}/{self.folder}/{self.db}.db" if self.folder else None
        return _url
