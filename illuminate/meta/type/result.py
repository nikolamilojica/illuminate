from __future__ import annotations

from typing import AsyncGenerator, Coroutine, Union

from illuminate.exporter import Exporter
from illuminate.observation import Observation
from illuminate.observer import Finding

Result = Union[
    AsyncGenerator[Union[Exporter, Finding, Observation], None],
    Coroutine,
]
