_ALEMBIC_ENV_PY = """
from logging.config import fileConfig
from pydoc import locate

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from bundesliga.settings import MODELS

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
        context.configure(connection=connection, target_metadata=target_metadata)

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
  postgres:
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
volumes:
  postgres:
    driver: local
    
"""

_EMPTY = """
"""

_FIXTURE_EXAMPLE = """
[
    {
    "name": "model",
    "data": [
        {
            "field": "Alice"
        },
        {
            "field": "Bob"
        }
    ]
    }
]
"""

_ILLUMINATE_MODEL = """
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Model(Base):
    __tablename__ = 'model'
    id = Column(Integer, primary_key=True)
    field = Column(String)
    
"""

_ILLUMINATE_SETTINGS = """
import os


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
    "{name}.models.example.Model",
]

NAME = "{name}"

"""

FILES = {
    "__init__.py": _EMPTY,
    "docker-compose.yaml": _DOCKER_COMPOSE,
    "settings.py": _ILLUMINATE_SETTINGS,
    "exporters/__init__.py": _EMPTY,
    "exporters/example.py": _EMPTY,
    "fixtures/example.json": _FIXTURE_EXAMPLE,
    "models/__init__.py": _EMPTY,
    "models/example.py": _ILLUMINATE_MODEL,
    "migrations/env.py": _ALEMBIC_ENV_PY,
    "migrations/script.py.mako": _ALEMBIC_SCRIPT_PY_MAKO,
    "migrations/versions/.gitkeep": _EMPTY,
    "observers/__init__.py": _EMPTY,
    "observers/example.py": _EMPTY,
}
