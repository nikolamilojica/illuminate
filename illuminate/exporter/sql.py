from loguru import logger

from illuminate.exceptions.exporter import BasicExporterException
from illuminate.exporter.exporter import Exporter


class SQLExporter(Exporter):
    """SQLExporter class, responsible for writing to destination"""

    def __init__(self, model):
        self.model = model

    def export(self, session, *args, **kwargs):
        """Load to destination"""
        session.add(self.model)
        try:
            session.commit()
        except Exception as exception:
            logger.critical(f'{self}.export(session="{session}") -> {exception}')
            raise BasicExporterException
        logger.success(f'{self}.export(session="{session}")')

    def __repr__(self):
        return f"SQLExporter(model={self.model})"
