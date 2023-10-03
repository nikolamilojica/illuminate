from __future__ import annotations

from typing import Iterable, Union

from aioinflux import InfluxDBClient  # type: ignore
from loguru import logger
from pandas import DataFrame  # type: ignore

from illuminate.exceptions import BasicExporterException
from illuminate.exporter import Exporter


class InfluxDBExporter(Exporter):
    """
    InfluxDBExporter class, writes data to InfluxDB database asynchronously.
    Inherits Exporter class and implements export method.

    Each InfluxDBExporter object is responsible for a single transaction with a
    single database. Attribute name is used to acquire database session object
    from Manager's sessions attribute.

    Constructor kwargs will be passed to client write method. For more
    information on write method, visit:
    https://aioinflux.readthedocs.io/en/stable/api.html

    Supported write data objects:
        - DataFrame with DatetimeIndex
        - Dict containing the keys: measurement, time, tags,
        fields
        - String (str or bytes) properly formatted in InfluxDB’s line protocol
        - An iterable of one of the above

    """

    name: str
    """
    InfluxDB database name selector used to get database session object from
    Manager.sessions attribute.
    """

    def __init__(
        self,
        points: Union[
            Union[DataFrame, dict, str, bytes],
            Iterable[Union[DataFrame, dict, str, bytes]],
        ],
        *args,
        **kwargs,
    ):
        """
        InfluxDBExporter's __init__ method.

        :param points: Supported data objects
        """
        self.params = kwargs
        self.points = points

    async def export(self, session: InfluxDBClient, *args, **kwargs) -> None:
        """
        Writes data to Influxdb asynchronously.

        :param session: InfluxDBClient object
        :return: None
        :raises BasicExporterException:
        """
        try:
            await session.write(self.points, **self.params)
        except Exception as exception:
            logger.warning(
                f'{self}.export(session="{session}") -> {exception}'
            )
            raise BasicExporterException
        logger.success(f'{self}.export(session="{session}")')

    def __repr__(self):
        """
        InfluxDBExporter's __repr__ method.

        :return: String representation of an instance
        """
        return f"InfluxDBExporter(points={self.points})"
