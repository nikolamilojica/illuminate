from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager
from typing import Callable, Union

from aiofile import async_open
from aiofile.utils import FileIOWrapperBase
from caio import thread_aio_asyncio
from loguru import logger

from illuminate.meta.type import Result
from illuminate.observation import Observation


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
        callback: Callable[[FileIOWrapperBase, tuple, dict], Result],
        *args,
        **kwargs,
    ):
        """
        FileObservation's __init__ method.

        :param url: File path
        :param callback: Async function/method that manipulates
        FileIOWrapperBase object and returns Result
        """
        super().__init__(url)
        self._callback = callback

    @asynccontextmanager
    async def observe(
        self, *args, **kwargs
    ) -> AsyncIterator[Union[None, Result]]:
        """
        Opens IO file stream asynchronously, pass stream object to a callback
        and returns None or Result as a context manager.

        :return: AsyncIterator with None or Result
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
