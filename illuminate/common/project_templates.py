_ADAPTER_EXAMPLE = """
from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import Type, Union

from illuminate.adapter import Adapter
from illuminate.observation import FileObservation
from illuminate.observation import HTTPObservation
from illuminate.observation import SQLObservation
from illuminate.observation import SplashObservation
from illuminate.observer import Finding

from exporters.example import ExporterInfluxDBExample
from exporters.example import ExporterSQLExample
from findings.example import FindingExample
from models.example import ModelExample


class AdapterExample(Adapter):
    \"\"\"
    Adapter class is responsible for turning Finding objects into Exporter or
    Observation objects, and yielding them when adapt method is called.

    It is also designated to be a place where any additional enrichment of data
    should be performed, calling external services with some async library. If
    additional data can be used to construct URL, additional Observations can
    be yielded. For more information how to yield Observation object, check
    {name}/observers/example.py.

    Attribute subscribers is a collection of Finding classes that will be
    processed by Adapter. If Finding is subscribed to two or more Adapters,
    priority in adaptation will be give to Adapter with higher priority score.

    Manager's instance (object that is running whole process) is passed as
    an argument when initializing Adapters. This allows Adapter object to
    interact with Manager object attributes, like database sessions or
    queues for advanced ETL flows, by simply asking for
    self.manager.sessions["postgresql"]["main"] to acquire async database
    session defined in {name}/settings.py.

    Note: Method adapt can not yield Findings.
    \"\"\"

    priority: int = 10
    subscribers: tuple[Type[Finding]] = (FindingExample,)

    async def adapt(
        self, finding: FindingExample, *args, **kwargs
    ) -> AsyncGenerator[
        Union[
            ExporterInfluxDBExample,
            ExporterSQLExample,
            FileObservation,
            HTTPObservation,
            SQLObservation,
            SplashObservation,
        ],
        None,
    ]:
        yield ExporterSQLExample(
            models=[
                ModelExample(
                    load_time=finding.load_time,
                    title=finding.title,
                    url=finding.url
                )
            ]
        )

        yield ExporterInfluxDBExample(
            points={{
                "measurement": "{name}",
                "tags": {{"url": finding.url, "title": finding.title}},
                "fields": {{"load_time": finding.load_time}},
            }}
        )

"""

_ALEMBIC_ENV_PY = """
from pydoc import locate

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from models.example import Base
from settings import MODELS

for model in MODELS:
    locate(model)

config = context.config


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={{"paramstyle": "named"}},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=Base.metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

"""

_ALEMBIC_SCRIPT_PY_MAKO = """
\"\"\"${{message}}

Revision ID: ${{up_revision}}
Revises: ${{down_revision | comma,n}}
Create Date: ${{create_date}}

\"\"\"
from alembic import op
import sqlalchemy as sa
${{imports if imports else ""}}

# revision identifiers, used by Alembic.
revision = ${{repr(up_revision)}}
down_revision = ${{repr(down_revision)}}
branch_labels = ${{repr(branch_labels)}}
depends_on = ${{repr(depends_on)}}


def upgrade():
    ${{upgrades if upgrades else "pass"}}


def downgrade():
    ${{downgrades if downgrades else "pass"}}

"""

_DOCKER_COMPOSE = """
version: '3.8'
services:
  grafana:
   image: grafana/grafana
   container_name: grafana
   restart: always
   depends_on:
     - influxdb
   environment:
     - GF_SECURITY_ADMIN_USER=illuminate
     - GF_SECURITY_ADMIN_PASSWORD=$ILLUMINATE_GRAFANA_PASSWORD
     - GF_INSTALL_PLUGINS=
   links:
     - influxdb
   ports:
     - '3000:3000'
   volumes:
     - grafana:/var/lib/grafana
  influxdb:
    image: influxdb:1.8
    container_name: influxdb
    restart: always
    environment:
      - INFLUXDB_ADMIN_USER=illuminate
      - INFLUXDB_ADMIN_PASSWORD=$ILLUMINATE_MEASUREMENTS_DB_PASSWORD
      - INFLUXDB_DB={name}
      - INFLUXDB_HTTP_AUTH_ENABLED=true
    ports:
      - '8086:8086'
    volumes:
      - influxdb:/var/lib/influxdb
  pg:
    container_name: pg
    image: postgres:latest
    restart: always
    environment:
      - POSTGRES_USER=illuminate
      - POSTGRES_PASSWORD=$ILLUMINATE_MAIN_DB_PASSWORD
      - POSTGRES_DB={name}
    ports:
      - '5432:5432'
    volumes:
      - postgres:/var/lib/postgresql/data
  pgadmin:
    container_name: pgadmin
    image: dpage/pgadmin4
    restart: always
    environment:
      - PGADMIN_DEFAULT_EMAIL=root@example.com
      - PGADMIN_DEFAULT_PASSWORD=$ILLUMINATE_PGADMIN_PASSWORD
    ports:
      - "8080:80"
  splash:
    container_name: splash
    image: scrapinghub/splash
    restart: always
    ports:
      - "8050:8050"
volumes:
  grafana:
    driver: local
  influxdb:
    driver: local
  postgres:
    driver: local

"""

_EMPTY = """
"""

_EXPORTER_EXAMPLE = """
from __future__ import annotations

from typing import Iterable, Union

from illuminate.exporter import InfluxDBExporter
from illuminate.exporter import SQLExporter
from pandas import DataFrame

from models.example import ModelExample


class ExporterInfluxDBExample(InfluxDBExporter):
    \"\"\"
    InfluxDBExporter class will write points to database using session. Points
    are passed at initialization, while database session is found by name
    attribute in the pool of existing sessions. Name must co-respond to DB
    section in {name}/settings.py. For more information how to initialize
    InfluxDBExporter class, check {name}/adapters/example.py
    \"\"\"

    name: str = "measurements"

    def __init__(
        self,
        points: Union[
            Union[DataFrame, dict, str, bytes],
            Iterable[Union[DataFrame, dict, str, bytes]],
        ],
    ):
        super().__init__(points)


class ExporterSQLExample(SQLExporter):
    \"\"\"
    SQLExporter class will commit models to database using session. Models are
    passed at initialization, while database session is found by name attribute
    in the pool of existing sessions. Name must co-respond to DB section in
    {name}/settings.py. For more information how to initialize SQLExporter
    class, check {name}/adapters/example.py
    \"\"\"

    name: str = "main"

    def __init__(self, models: Union[list[ModelExample], tuple[ModelExample]]):
        super().__init__(models)

"""

_FIXTURE_EXAMPLE = """
[
    {{
    "name": "{name}",
    "data": [
        {{
            "load_time": "1.0",
            "url": "https://webscraper.io/",
            "title": "Web Scraper - The #1 web scraping extension"
        }},
        {{
            "load_time": "1.0",
            "url": "https://webscraper.io/tutorials",
            "title": "Web Scraper Tutorials"
        }}
    ]
    }}
]
"""

_MODELS = """
from sqlalchemy.orm import declarative_base

Base = declarative_base()

"""

_MODEL_EXAMPLE = """
from sqlalchemy import Column, Float, Integer, String

from models import Base


class ModelExample(Base):
    \"\"\"
    SQLAlchemy model used by SQLExporter object. For more information about
    SQLExporter class check {name}/exporters/example.py.
    \"\"\"

    __tablename__ = "{name}"
    id: int = Column(Integer, primary_key=True)
    load_time: float = Column(Float)
    title: str = Column(String)
    url: str = Column(String)

    def __repr__(self):
        \"\"\"ModelExample's __repr__ method.\"\"\"
        return (
            f'ModelExample(load_time={{self.load_time}},'
            f'title="{{self.title}}",url="{{self.url}}")'
        )

"""

_ILLUMINATE_SETTINGS = """
\"\"\"
This file represents project {name}'s settings. It will be imported by a
framework and used to configure run. The sections are as following:

* CONCURRENCY
Number of workers per queue type. I/O heavy queues can have more workers
assigned to them to exploit longer wait times.

* DB
Database related data used by SQLAlchemy to acquire sessions. Sessions are
obtained at the start of the ETL process and can be accessed by instantiating
Manager class and access sessions attribute.

* MODELS
List of SQLAlchemy models affected by illuminate cli when invoking
'db revision', 'db upgrade' and 'db populate' commands.

* NAME
Project name.

* OBSERVATION_CONFIGURATION
General and Observation type specific configuration. Type specific
configuration is used if Observation is not specifying its own.
\"\"\"

import os

from illuminate import __version__

CONCURRENCY = {{
    "observers": 8,
    "adapters": 2,
    "exporters": 8,
}}

DB = {{
    "main": {{
        "host": "localhost",
        "pass": os.environ.get("ILLUMINATE_MAIN_DB_PASSWORD"),
        "port": "5432",
        "user": "illuminate",
        "type": "postgresql",
    }},
    "measurements": {{
        "host": "localhost",
        "pass": os.environ.get("ILLUMINATE_MEASUREMENTS_DB_PASSWORD"),
        "port": "8086",
        "user": "illuminate",
        "type": "influxdb",
    }},
}}

MODELS = [
    "models.example.ModelExample",
]

NAME = "{name}"

OBSERVATION_CONFIGURATION = {{
    "delay": 0.1,
    "http": {{
        "auth_username": None,
        "auth_password": None,
        "connect_timeout": 10.0,
        "body": None,
        "headers": None,
        "method": "GET",
        "request_timeout": 10.0,
        "user_agent": f"Illuminate-bot/{{__version__}}",
        "validate_cert": False,
    }},
    "splash": {{
        "body": "",
        "host": "localhost",
        "method": "GET",
        "port": 8050,
        "protocol": "http",
        "render": "html",
        "timeout": 30,
    }}
}}

"""

_FINDING_EXAMPLE = """
from dataclasses import dataclass
from dataclasses import field

from illuminate.observer import Finding


@dataclass(frozen=True, order=True)
class FindingExample(Finding):
    \"\"\"
    Finding is a data class, meant to hold raw data extracted by Observation's
    callback. Finding will be passed to Adapter object's adapt method if
    it is subscribed to Adapter.

    Check {name}/adapters/example.py to learn more about subscription.
    \"\"\"

    load_time: float = field()
    title: str = field()
    url: str = field()

"""

_OBSERVER_EXAMPLE = """
from __future__ import annotations

from collections.abc import AsyncGenerator, Generator
from typing import Optional, Union
from urllib.parse import urldefrag
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from illuminate.manager import Manager
from illuminate.observation import HTTPObservation
from illuminate.observer import Observer
from tornado.httpclient import HTTPResponse

from exporters.example import ExporterInfluxDBExample
from exporters.example import ExporterSQLExample
from findings.example import FindingExample


def _create_soup(response: HTTPResponse) -> BeautifulSoup:
    html = response.body.decode(errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    return soup


def _extract_hrefs(
    soup: BeautifulSoup, url: str
) -> Generator[str, None]:
    links = soup.find_all("a")
    for link in links:
        _url = link.get("href")
        if _url:
            yield urljoin(url, urldefrag(_url)[0])


class ObserverExample(Observer):
    \"\"\"
    Observer is ETL configuration class. It represents entry point, and it
    defines the flow with observe, and any additional method.

    Once initialized by the framework, it will fill an observation queue with
    objects from Observer's initial_observation collection, starting the whole
    process.

    Note: Multiple Observers can exist in the same project.
    \"\"\"

    ALLOWED: Union[list[str], tuple[str]] = ("https://webscraper.io/",)
    \"\"\"
    Collection of strings evaluated against URL to determent if URL is allowed
    to be observed. If empty, no Observation wide restrictions are forced.
    \"\"\"
    NAME: str = "example"
    \"\"\"Observer's name.\"\"\"

    def __init__(self, manager: Optional[Manager] = None):
        \"\"\"
        Collection initial_observations is de facto entry point. It must
        contain Observation objects initialized with URL, allowed list of
        strings and callback method. If Observation's URL starts with element
        in allowed collection, it will be performed. Otherwise, it is
        rejected.

        Manager's instance (object that is running whole process) is passed as
        an argument when initializing Observers. This allows Observer object to
        interact with Manager object attributes, like database sessions or
        queues for advanced ETL flows, by simply asking for
        self.manager.sessions["postgresql"]["main"] to acquire async database
        session defined in {name}/settings.py.
        \"\"\"

        super().__init__(manager)
        self.initial_observations = [
            HTTPObservation(
                "https://webscraper.io/",
                allowed=self.ALLOWED,
                callback=self.observe,
            ),
        ]

    async def observe(
        self, response: HTTPResponse, *args, **kwargs
    ) -> AsyncGenerator[
        Union[
            ExporterInfluxDBExample,
            ExporterSQLExample,
            FindingExample,
            HTTPObservation,
        ],
        None,
    ]:
        \"\"\"
        ETL flow is regulated by a yielded object type of Observation's
        callback method. Each object type corresponds to ETL stage:

        * Observation -> Extract
        * Finding -> Transform
        * Exporter -> Load

        In the example below, initial HTTPObservation returned Tornado's
        HTTP response object that was used to extract all hrefs from HTML.
        These hrefs will be used as URLs for new HTTPObservations, using
        the same observe method as a callback and same allowed collection.
        Finally, Finding object is yielded, representing a desired data.

        This flow, with everything set, represents a simple web scraper that
        will visit every page found on a domain, and take page's title and URL
        as desired data.

        Tip: If there is no need for some further data enrichment or
        manipulation, yield Exporter object instead of Finding object.
        For reference check {name}/adapters/example.py.

        Note: Illuminate takes care of tracking what resources were already
        requested, avoiding duplication. Resource check pool is shared between
        Observers, avoiding overlapping.
        \"\"\"

        soup = _create_soup(response)
        hrefs = _extract_hrefs(soup, response.effective_url)
        for href in hrefs:
            yield HTTPObservation(
                href,
                allowed=self.ALLOWED,
                callback=self.observe,
            )
        yield FindingExample(
            response.request_time,
            soup.title.text,
            response.effective_url
        )

"""

FILES = {
    "docker-compose.yaml": _DOCKER_COMPOSE,
    "settings.py": _ILLUMINATE_SETTINGS,
    "adapters/__init__.py": _EMPTY,
    "adapters/example.py": _ADAPTER_EXAMPLE,
    "exporters/__init__.py": _EMPTY,
    "exporters/example.py": _EXPORTER_EXAMPLE,
    "fixtures/example.json": _FIXTURE_EXAMPLE,
    "models/__init__.py": _MODELS,
    "models/example.py": _MODEL_EXAMPLE,
    "migrations/env.py": _ALEMBIC_ENV_PY,
    "migrations/script.py.mako": _ALEMBIC_SCRIPT_PY_MAKO,
    "migrations/versions/.gitkeep": _EMPTY,
    "findings/__init__.py": _EMPTY,
    "observers/__init__.py": _EMPTY,
    "findings/example.py": _FINDING_EXAMPLE,
    "observers/example.py": _OBSERVER_EXAMPLE,
}
