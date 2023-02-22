from __future__ import annotations

from collections.abc import AsyncGenerator
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack
from contextlib import asynccontextmanager
from typing import Callable, Optional, Union

from aiofile import async_open
from aiofile.utils import FileIOWrapperBase
from caio import thread_aio_asyncio
from loguru import logger

from illuminate.exporter import Exporter
from illuminate.observation import Observation
from illuminate.observer import Finding


class FileObservation(Observation):
    """
    FileObservation class, reads file content asynchronously. Inherits
    Observation class and implements observe method.
    """

    def __hash__(self) -> int:
        """
        FileObservation object hash value.

        :return: int
        """
        return hash(self.url)

    def __init__(
        self,
        url: str,
        /,
        callback: Callable[
            [FileIOWrapperBase, tuple, dict],
            AsyncGenerator[Union[Exporter, Finding, Observation], None],
        ],
        *args,
        **kwargs,
    ):
        """
        FileObservation's __init__ method.

        :param url: File path
        :param callback: Async function/method that will manipulate file
        object and yield Exporter, Finding and Observation objects
        """
        super().__init__(url)
        self._callback = callback

    @asynccontextmanager
    async def observe(
        self, *args, **kwargs
    ) -> AsyncIterator[
        Optional[AsyncGenerator[Union[Exporter, Finding, Observation], None]]
    ]:
        """
        Opens IO file stream asynchronously, pass stream object to a callback
        and yields async Exporter, Finding, and Observation object generator
        if read is successful.

        :return: Async Exporter, Finding, and Observation object generator or
        None
        """
        _file = None
        _items = None
        async with AsyncExitStack() as stack:
            context = await stack.enter_async_context(
                thread_aio_asyncio.AsyncioContext()
            )
            try:
                _file = await stack.enter_async_context(
                    async_open(self.url, "r", context=context)
                )
                logger.info(f"{self}.observe() -> {_file}")
                _items = self._callback(_file, *args, **kwargs)
            except FileNotFoundError as exception:
                logger.warning(f"{self}.observe() -> {exception}")
            except Exception as exception:
                logger.critical(f"{self}.observe() -> {exception}")
            finally:
                yield _items
                if _file:
                    await _file.close()

    def __repr__(self):
        """
        FileObservation's __repr__ method.

        :return: String representation of an instance
        """
        return f'FileObservation("{self.url}",callback="{self._callback}")'
