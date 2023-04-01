from illuminate.exceptions import BasicExporterException
from illuminate.interface import IExporter


class Exporter(IExporter):
    """
    Exporter class, writes data to destination. Class must be inherited and
    method export must be implemented in a child class.
    """

    async def export(self, *args, **kwargs):
        """
        Writes data to destination. Must be implemented in a child class.

        :return: None
        :raises BasicExporterException:
        """
        raise BasicExporterException(
            "Method export must be implemented in child class"
        )
