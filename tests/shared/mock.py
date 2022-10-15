from illuminate.observation.http import HTTPObservation
from illuminate.observer.observer import Observer as _Observer


class Observer(_Observer):
    """Dummy Observer"""

    NAME = "example"

    def __init__(self):
        super().__init__()
        self.initial_observations = [
            HTTPObservation(
                "https://webscraper.io/",
                allowed=("https://webscraper.io/",),
                callback=self.observe,
            ),
        ]

    def observe(self, response, *args, **kwargs):
        """Abstract method implementation"""


class Settings:
    """Dummy Manager settings"""

    def __init__(self, name):
        self.CONCURRENCY = {}
        self.DB = {}
        self.MODELS = []
        self.NAME = name
        self.OBSERVATION_CONFIGURATION = {}
