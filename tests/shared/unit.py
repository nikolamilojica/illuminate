import os
import sys
import tempfile
from contextlib import contextmanager

from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker


class Test:
    """
    Test class with path context manager that provides tests with temporary
    directory placed on PYTHONPATH with sqlite database attached.
    """

    db = "test"
    folder = None

    @staticmethod
    def assert_project_structure(name, files, path, cwd=False):
        """
        Assert project structure.

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
        Creates database engine.

        :return: sqlalchemy.engine.Engine or None
        """
        return create_engine(self.url) if self.url else None

    @property
    def engine_async(self):
        """
        Creates async database engine.

        :return: sqlalchemy.ext.asyncio.engine.AsyncEngine or None
        """
        return create_async_engine(self.url_async) if self.url_async else None

    @contextmanager
    def path(self):
        """
        Put temporary directory path to PYTHONPATH, set it as cwd and clean
        imports once the test is finished.

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
        Create database session.

        :return: sqlalchemy.orm.Session or None
        """
        return sessionmaker(self.engine)() if self.url else None

    @property
    def session_async(self):
        """
        Create async database session.

        :return: sqlalchemy.ext.asyncio.session.AsyncSession or None
        """
        return (
            sessionmaker(
                self.engine_async,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            if self.url_async
            else None
        )

    @property
    def url(self):
        """
        Create database URL.

        :return: str or None
        """
        _url = f"sqlite:///{self.folder}/{self.db}.db" if self.folder else None
        return _url

    @property
    def url_async(self):
        """
        Create async database URL.

        :return: str or None
        """
        _url = (
            f"sqlite+aiosqlite:///{self.folder}/{self.db}.db"
            if self.folder
            else None
        )
        return _url
