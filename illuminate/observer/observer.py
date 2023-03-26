from __future__ import annotations

from typing import Optional, Union, TYPE_CHECKING

from aiofile.utils import FileIOWrapperBase
from sqlalchemy.engine.result import Result
from tornado.httpclient import HTTPResponse

from illuminate.exceptions import BasicObserverException
from illuminate.interface import IObserver
from illuminate.observation import Observation

if TYPE_CHECKING:
    from illuminate.manager import Manager


class Observer(IObserver):
    """
    Observer class, controls ETL process by implementing observe and other
    methods that will be used as callbacks in Observation class children's
    observe method.
    """

    NAME: str
    """Observer name."""

    def __init__(self, manager: Optional[Manager] = None):
        """
        Observer's __init__ method.

        :param manager: Manager object
        """
        self.initial_observations: list[Observation] = []
        self.manager = manager

    async def observe(
        self,
        response: Union[FileIOWrapperBase, HTTPResponse, Result],
        *args,
        **kwargs
    ):
        """
        Manipulates response object and yields Exporter, Finding and
        Observation objects.

        :param response: HTTP response object
        :return: Async Exporter, Finding, and Observation object generator
        """
        raise BasicObserverException(
            "Method observe must be implemented in child class"
        )
