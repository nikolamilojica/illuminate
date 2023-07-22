import pytest
from aioinflux import InfluxDBClient

from illuminate.exceptions import BasicExporterException
from illuminate.exporter import InfluxDBExporter
from tests.unit import Test


class TestExporterInfluxDB(Test):

    conf = {
        "host": "localhost",
        "port": 8086,
        "db": "test",
        "username": "username",
        "password": "password",
    }

    @pytest.mark.asyncio
    @pytest.mark.xfail(raises=BasicExporterException)
    async def test_export_unsuccessfully(self):
        """
        Given: Database session object is created but database is unavailable
        When: Exporting points and process fails
        Expected: BasicExporterException is raised
        """
        with pytest.raises(BasicExporterException):
            exporter = InfluxDBExporter(points={})
            async with InfluxDBClient(**self.conf) as session:
                await exporter.export(session)

    @pytest.mark.asyncio
    async def test_export_successfully(self, async_influxdb_write):
        """
        Given: Database session object is created
        When: Exporting points
        Expected: Data is placed in database

        Note: Until docker containers are not part of test process, this code
        is not testable
        """
        exporter = InfluxDBExporter(points={})
        async with InfluxDBClient(**self.conf) as session:
            await exporter.export(session)
