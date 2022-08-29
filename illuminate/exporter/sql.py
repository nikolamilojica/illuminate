from loguru import logger

from illuminate.exporter.exporter import Exporter


class SQLExporter(Exporter):
    """SQLExporter class, responsible for writing to destination"""

    def __init__(self, model):
        self.model = model

    def export(self, session, *args, **kwargs):
        """Load to destination"""
        session.add(self.model)
        session.commit()  # TODO: try/catch
        logger.info(f'{self}.export(session="{session}")')

    def __repr__(self):
        return f"SQLExporter(model={self.model})"
