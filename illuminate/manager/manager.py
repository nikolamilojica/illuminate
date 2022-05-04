import os

from illuminate.common.project_templates import FILES
from illuminate.discrete.manager.interface import Interface
from illuminate.exceptions.manager import BasicManagerException
from illuminate.meta.singleton import Singleton


class Manager(Interface, metaclass=Singleton):
    def __init__(self, name=None, path=None, *args, **kwargs):
        self.name = name
        self.path = path

    @classmethod
    def setup(cls, name, path, *args, **kwargs):
        """Create project directory and populates it with project files"""

        path = os.path.join(path, name)
        if os.path.exists(path):
            raise BasicManagerException

        os.mkdir(path)
        sep = "/"

        for name, content in FILES.items():
            file_path = os.path.join(path, name)
            if sep in name:
                os.makedirs(sep.join(file_path.split(sep)[:-1]), exist_ok=True)
            with open(file_path, "w") as file:
                file.write(f"{content.strip()}\n")
