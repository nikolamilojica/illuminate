_ADAPTER_EXAMPLE = """
from illuminate.adapter.adapter import Adapter

from exporters.example import ExporterExample
from findings.example import FindingExample
from models.example import ModelExample


class AdapterExample(Adapter):
    subscribers = (FindingExample,)

    async def adapt(self, finding, *args, **kwargs):
        yield ExporterExample(
            model=ModelExample(title=finding.title, url=finding.url)
        )

"""

_ALEMBIC_ENV_PY = """
from logging.config import fileConfig
from pydoc import locate

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from settings import MODELS

config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = [locate(i).metadata for i in MODELS]


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
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
            connection=connection,
            target_metadata=target_metadata
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
volumes:
  postgres:
    driver: local

"""

_EMPTY = """
"""

_EXPORTER_EXAMPLE = """
from illuminate.exporter.sql import SQLExporter


class ExporterExample(SQLExporter):
    def __init__(self, model):
        super().__init__(model)
        self.name = "main"
        self.type = "postgresql"

"""

_FIXTURE_EXAMPLE = """
[
    {{
    "name": "{name}",
    "data": [
        {{
            "url": "https://webscraper.io/",
            "title": "Web Scraper - The #1 web scraping extension"
        }},
        {{
            "url": "https://webscraper.io/tutorials",
            "title": "Web Scraper Tutorials"
        }}
    ]
    }}
]
"""

_MODEL_EXAMPLE = """
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class ModelExample(Base):
    __tablename__ = "{name}"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)

    def __repr__(self):
        return f'ModelExample(title="{{self.title}}",url="{{self.url}}")'

"""

_ILLUMINATE_SETTINGS = """
import os


CONCURRENCY = {{
    "observers": 8,
    "adapters": 2,
    "exporters": 16,
}}

DB = {{
    "main": {{
        "host": "localhost",
        "pass": os.environ.get("ILLUMINATE_MAIN_DB_PASSWORD"),
        "port": "5432",
        "user": "illuminate",
        "type": "postgresql",
    }}
}}

MODELS = [
    "models.example.ModelExample",
]

NAME = "{name}"

OBSERVER_CONFIGURATION = {{
    "delay": .1,
    "http": {{
        "auth_username": None,
        "auth_password": None,
        "connect_timeout": 10.0,
        "body": None,
        "headers": None,
        "method": "GET",
        "request_timeout": 10.0,
        "user_agent": "Illuminate ETL Bot -- {name}",
    }}
}}

"""

_FINDING_EXAMPLE = """
from dataclasses import dataclass
from dataclasses import field

from illuminate.observer.finding import Finding


@dataclass(frozen=True, order=True)
class FindingExample(Finding):
    title: str = field()
    url: str = field()

"""

_OBSERVER_EXAMPLE = """
from urllib.parse import urldefrag
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from illuminate.observation.http import HTTPObservation
from illuminate.manager.manager import Manager
from illuminate.observer.observer import Observer

from findings.example import FindingExample


async def _create_soup(response):
    html = response.body.decode(errors="ignore")
    soup = BeautifulSoup(html, "html.parser")
    return soup


async def _extract_hrefs(soup, url):
    links = soup.find_all("a")
    for link in links:
        _url = link.get("href")
        if _url:
            yield urljoin(url, urldefrag(_url)[0])


class ObserverExample(Observer):
    ALLOWED = ("https://webscraper.io/",)
    NAME = "example"

    def __init__(self):
        super().__init__()
        self._manager = Manager()
        self.initial_observations = [
            HTTPObservation(
                "https://webscraper.io/",
                allowed=self.ALLOWED,
                callback=self.observe,
            ),
        ]

    async def observe(self, response, *args, **kwargs):
        soup = await _create_soup(response)
        hrefs = _extract_hrefs(soup, response.effective_url)
        async for href in hrefs:
            yield HTTPObservation(
                href,
                allowed=self.ALLOWED,
                callback=self.resume,
            )
        yield FindingExample(soup.title.text, response.effective_url)

    async def resume(self, response, *args, **kwargs):
        soup = await _create_soup(response)
        hrefs = _extract_hrefs(soup, response.effective_url)
        async for href in hrefs:
            yield HTTPObservation(
                href,
                allowed=self.ALLOWED,
                callback=self.resume,
            )
        yield FindingExample(soup.title.text, response.effective_url)

"""

FILES = {
    "__init__.py": _EMPTY,
    "docker-compose.yaml": _DOCKER_COMPOSE,
    "settings.py": _ILLUMINATE_SETTINGS,
    "adapters/__init__.py": _EMPTY,
    "adapters/example.py": _ADAPTER_EXAMPLE,
    "exporters/__init__.py": _EMPTY,
    "exporters/example.py": _EXPORTER_EXAMPLE,
    "fixtures/example.json": _FIXTURE_EXAMPLE,
    "models/__init__.py": _EMPTY,
    "models/example.py": _MODEL_EXAMPLE,
    "migrations/env.py": _ALEMBIC_ENV_PY,
    "migrations/script.py.mako": _ALEMBIC_SCRIPT_PY_MAKO,
    "migrations/versions/.gitkeep": _EMPTY,
    "findings/__init__.py": _EMPTY,
    "observers/__init__.py": _EMPTY,
    "findings/example.py": _FINDING_EXAMPLE,
    "observers/example.py": _OBSERVER_EXAMPLE,
}
