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

        if path != ".":
            path = os.path.join(path, name)
            if os.path.exists(path):
                raise BasicManagerException
            os.mkdir(path)

        for _name, content in FILES.items():
            file_path = os.path.join(path, _name)
            if os.sep in _name:
                os.makedirs(os.sep.join(file_path.split(os.sep)[:-1]), exist_ok=True)
            with open(file_path, "w") as file:
                file.write(f"{content.format(name=name).strip()}\n")
