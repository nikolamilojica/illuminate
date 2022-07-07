from illuminate.exporter.exporter import Exporter


class SQLExporter(Exporter):
    """SQLExporter class, responsible for writing to destination"""
    def __init__(self, model):
        self.model = model

    def export(self, session, *args, **kwargs):
        """Load to destination"""
        session.add(self.model)
        session.commit()
        print(self.model)
