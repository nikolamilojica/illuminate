<p style="text-align: justify">If you have followed steps from the home page, and created a
project inside a <code>tutorial/</code> directory there will be the following
project structure inside that directory.</p>


    tutorial
    ├── adapters
    │   ├── __init__.py
    │   └── example.py
    ├── exporters
    │   ├── __init__.py
    │   └── example.py
    ├── findings
    │   ├── __init__.py
    │   └── example.py
    ├── fixtures
    │   └── example.json
    ├── migrations
    │   ├── versions
    │   ├── env.py
    │   └── script.py.mako
    ├── models
    │   ├── __init__.py
    │   └── example.py
    ├── observers
    │   ├── __init__.py
    │   └── example.py
    ├── docker-compose.yaml
    └── settings.py

## Observers

<p style="text-align: justify"><code>observers/</code> package is a place
where you write your ETL configuration classes.</p>

<p style="text-align: justify">Once <code>illuminate observe start</code>
command is issued, all classes found in the package which name starts with the
word "Observer" will be added into context and initialized.</p>

```python
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
    """
    Observer is ETL configuration class. It represents entry point, and it
    defines the flow with observe, and any additional method.

    Once initialized by the framework, it will fill an observation queue with
    objects from Observer's initial_observation collection, starting the whole
    process.

    Note: Multiple Observers can exist in the same project.
    """

    ALLOWED: Union[list[str], tuple[str]] = ("https://webscraper.io/",)
    """
    Collection of strings evaluated against URL to determent if URL is allowed
    to be observed. If empty, no Observation wide restrictions are forced.
    """
    LABELS: dict = {"tag": "example"}
    """Observer's labels."""
    NAME: str = "example"
    """Observer's name."""

    def __init__(self, manager: Optional[Manager] = None):
        """
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
        session defined in tutorial/settings.py.
        """

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
        """
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
        For reference check tutorial/adapters/example.py.

        Note: Illuminate takes care of tracking what resources were already
        requested, avoiding duplication. Resource check pool is shared between
        Observers, avoiding overlapping.
        """

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
```

### `Observer` vs `Observation`
<p style="text-align: justify"><code>Observer</code> is ETL configuration
class. It introduces <code>Observation</code> objects, in this case
<code>HTTPObservation</code> objects, through
<code>initial_observations</code>, to a framework. It also should be used
(not forced, but suggested) to contain all callback methods used by
<code>Observation</code> objects.</p>

<p style="text-align: justify"><code>Observation</code> class is a type of
source that will be read. Once the data is pulled, it will provide a response
object to a callback function that will asynchronously generate additional
object related to ETL flow, using Illuminate ETL Mapping Classes.</p>

> **NOTE**: You can register any async generator as `HTTPObservation.callback`.
For simplicity, we will use `ObserverExample.observe` method.

#### ETL Mapping Classes

<p style="text-align: justify">Each stage in ETL flow is represented by a
class from Illuminate framework.</p>

- Extract is represented with `Observation`
- Transform is represented with `Adapter`
- Load is represented with `Exporter`

<p style="text-align: justify">If a response object from initial
<code>Observation</code> is just a step before the data you want to export,
yield new <code>Observation</code> with same or different callback, allowing
you to construct a complex set of rules.</p>

<p style="text-align: justify">If a response object holds the data you want to
adapt, yield <code>Finding</code> object. It will be picked up by
<code>Adapter</code> instances that will perform <code>adapt</code> method with
<code>Finding</code> object passed as argument if the condition is met.</p>

<p style="text-align: justify">If a response object is something that
requires minimal transformation, or it could be used raw, you can yield
<code>Exporter</code> object and skip complex adaptation.</p>

## Findings
<p style="text-align: justify"><code>findings/</code> package is a place
where you write your data classes.</p>

<p style="text-align: justify">This class is meant to be picked up by a
framework and passed to <code>Adapter</code> instance, to perform actual
adaptation up on data, and yield <code>Exporter</code> or
<code>Observation</code> objects.</p>

<p style="text-align: justify">It can only be yielded by
<code>Observation</code> object's <code>callback</code>, in our example
project, it will be yield by<code>ExampleObserver.observe</code> method.</p>

```python
from dataclasses import dataclass
from dataclasses import field

from illuminate.observer import Finding


@dataclass(frozen=True, order=True)
class FindingExample(Finding):
    """
    Finding is a data class, meant to hold raw data extracted by Observation's
    callback. Finding will be passed to Adapter object's adapt method if
    it is subscribed to Adapter.

    Check tutorial/adapters/example.py to learn more about subscription.
    """

    load_time: float = field()
    title: str = field()
    url: str = field()
```

## Model
<p style="text-align: justify"><code>models/</code> package is a place where
you write your database model classes.</p>

<p style="text-align: justify">Models are used by <code>SQLExporter</code> in
our example and are recommended method of writing and reading data from SQL
database.</p>

> **NOTE**: `SQLObservation` class is not yet introduced to the framework.

```python
from sqlalchemy import Column, Float, Integer, String

from models import Base


class ModelExample(Base):
    """
    SQLAlchemy model used by SQLExporter object. For more information about
    SQLExporter class check tutorial/exporters/example.py.
    """

    __tablename__ = "tutorial"
    id: int = Column(Integer, primary_key=True)
    load_time: float = Column(Float)
    title: str = Column(String)
    url: str = Column(String)

    def __repr__(self):
        """ModelExample's __repr__ method."""
        return (
            f'ModelExample(load_time={self.load_time},'
            f'title="{self.title}",url="{self.url}")'
        )
```


## Adapter
<p style="text-align: justify"><code>adapters/</code> package is a place where
you write your transformation classes.</p>

<p style="text-align: justify">Once <code>illuminate observe start</code>
command is issued, all classes found in the package which name starts with the
word "Adapter" will be added into context and initialized.</p>

<p style="text-align: justify">Once the framework gets <code>Finding</code>
object from a queue, it will check if object is "subscribed" to
<code>Adapter</code>. If object is subscribed, the framework will pass it to
<code>adapt</code> method that will yield <code>Exporter</code> or
<code>Observation</code> objects.</p>

<p style="text-align: justify">Method <code>adapt</code> is where you implement
your adaptation rules. In the following example, method <code>adapt</code> is
just used to create a model instance to be passed to <code>SQLExpoter</code>
instance, yet to be saved later into the database.</p>

<p style="text-align: justify">Each <code>Adapter</code> object must contain a
tuple of <code>Finding</code> classes, called <code>subscribers</code> that
will be passed to<code>adapt</code> method. Others will be rejected by a
framework.</p>

<p style="text-align: justify">Since there could be multiple Adapter classes
with various implementation of  <code>adapt</code> method, if
<code>Finding</code> is subscribed to multiple <code>Adapters</code>,
<code>priority</code> attribute will determent which <code>adapt</code> method
should be called first.</p>

> **NOTE**: Method `adapt` can't yield <code>Findings</code>.</p>

```python
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
    """
    Adapter class is responsible for turning Finding objects into Exporter or
    Observation objects, and yielding them when adapt method is called.

    It is also designated to be a place where any additional enrichment of data
    should be performed, calling external services with some async library. If
    additional data can be used to construct URL, additional Observations can
    be yielded. For more information how to yield Observation object, check
    tutorial/observers/example.py.

    Attribute subscribers is a collection of Finding classes that will be
    processed by Adapter. If Finding is subscribed to two or more Adapters,
    priority in adaptation will be give to Adapter with higher priority score.

    Manager's instance (object that is running whole process) is passed as
    an argument when initializing Adapters. This allows Adapter object to
    interact with Manager object attributes, like database sessions or
    queues for advanced ETL flows, by simply asking for
    self.manager.sessions["postgresql"]["main"] to acquire async database
    session defined in tutorial/settings.py.

    Note: Method adapt can not yield Findings.
    """

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
            points={
                "measurement": "tutorial",
                "tags": {"url": finding.url, "title": finding.title},
                "fields": {"load_time": finding.load_time},
            }
        )
```


## Exporter
<p style="text-align: justify"><code>exporters/</code> package is a place where
you write your dump classes.</p>

```python
from __future__ import annotations

from typing import Iterable, Union

from illuminate.exporter import InfluxDBExporter
from illuminate.exporter import SQLExporter
from pandas import DataFrame

from models.example import ModelExample


class ExporterInfluxDBExample(InfluxDBExporter):
    """
    InfluxDBExporter class will write points to database using session. Points
    are passed at initialization, while database session is found by name
    attribute in the pool of existing sessions. Name must co-respond to DB
    section in tutorial/settings.py. For more information how to initialize
    InfluxDBExporter class, check tutorial/adapters/example.py
    """

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
    """
    SQLExporter class will commit models to database using session. Models are
    passed at initialization, while database session is found by name attribute
    in the pool of existing sessions. Name must co-respond to DB section in
    tutorial/settings.py. For more information how to initialize SQLExporter
    class, check tutorial/adapters/example.py
    """

    name: str = "main"

    def __init__(self, models: Union[list[ModelExample], tuple[ModelExample]]):
        super().__init__(models)
```

<p style="text-align: justify">In our example, everything is set for
<code>Exporter</code> object to fetch a database connection from the framework
and use it to facilitate dump to the destination. Since we are writing to SQL
database, we will import <code>SQLExporter</code> to inherit from in
<code>ExporterExample</code> class.</p>

## Migrations
<p style="text-align: justify"><code>migrations/</code> package contains files needed by
<a href="https://alembic.sqlalchemy.org/en/latest/">Alembic</a>
to perform database operations. It contains <code>versions</code> directory
where migration scripts are held, providing Illuminate with the ability to
administer its own databases out of the box.</p>

<p style="text-align: justify">Usually, the content of this directory is not a
user's concern.</p>

## Fixtures
<p style="text-align: justify">Directory <code>fixtures/</code> holds json files that contain
data needed in ETL flow beforehand. This data is injected into the database
with <code>illuminate manage database populate</code> cli command.</p>

<p style="text-align: justify">Each object in a list represents a table/model.
Key <code>name</code> represents table/model name and <code>data</code> is a
list of rows to be inserted with CLI command.</p>

```json
[
    {
    "name": "tutorial",
    "data": [
        {
            "load_time": "1.0",
            "url": "https://webscraper.io/",
            "title": "Web Scraper - The #1 web scraping extension"
        },
        {
            "load_time": "1.0",
            "url": "https://webscraper.io/tutorials",
            "title": "Web Scraper Tutorials"
        }
    ]
    }
]
```

## Settings
<p style="text-align: justify">Module <code>settings.py</code> contains all configuration
needed to run ETL process.</p>

```python
"""
This file represents project tutorial's settings. It will be imported by a
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
"""

import os

from illuminate import __version__

CONCURRENCY = {
    "adapters": 2,
    "exporters": 8,
    "observations": 8,
}

DB = {
    "main": {
        "host": "localhost",
        "name": "tutorial",
        "pass": os.environ.get("ILLUMINATE_MAIN_DB_PASSWORD"),
        "port": "5432",
        "user": "illuminate",
        "type": "postgresql",
    },
    "measurements": {
        "host": "localhost",
        "name": "tutorial",
        "pass": os.environ.get("ILLUMINATE_MEASUREMENTS_DB_PASSWORD"),
        "port": "8086",
        "user": "illuminate",
        "type": "influxdb",
    },
}

MODELS = [
    "models.example.ModelExample",
]

NAME = "tutorial"

OBSERVATION_CONFIGURATION = {
    "delay": 0.1,
    "http": {
        "auth_username": None,
        "auth_password": None,
        "connect_timeout": 10.0,
        "body": None,
        "headers": None,
        "method": "GET",
        "request_timeout": 10.0,
        "user_agent": f"Illuminate-bot/{__version__}",
        "validate_cert": False,
    },
    "splash": {
        "body": "",
        "host": "localhost",
        "method": "GET",
        "port": 8050,
        "protocol": "http",
        "render": "html",
        "timeout": 30,
    }
}
```

## Environment
<p style="text-align: justify">Environment for a development purposes is
provided by docker-compose.yaml file. It will spin up postgres database and
pgadmin containers to monitor your flow on your localhost.</p>

> **NOTE**: As additional Observations and Exporters are added, this file will
> grow as well.

```yaml
version: '3.8'
services:
  influxdb:
    image: influxdb:1.8
    container_name: influxdb
    restart: always
    environment:
      - INFLUXDB_ADMIN_USER=illuminate
      - INFLUXDB_ADMIN_PASSWORD=$ILLUMINATE_MEASUREMENTS_DB_PASSWORD
      - INFLUXDB_DB=tutorial
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
      - POSTGRES_DB=tutorial
    ports:
      - '5432:5432'
    volumes:
      - postgres:/var/lib/postgresql/data
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
```
