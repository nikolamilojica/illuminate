# Illuminate

[![Code Style: Black](
https://img.shields.io/badge/code%20style-black-000000.svg)](
https://github.com/psf/black)
[![Coveralls Coverage](
https://coveralls.io/repos/github/nikolamilojica/illuminate/badge.svg?branch=master&t=YU1NaL)](
https://coveralls.io/github/nikolamilojica/illuminate?branch=master)
[![GitHub Actions - Tests Workflow](
https://github.com/nikolamilojica/illuminate/actions/workflows/tests.yaml/badge.svg?branch=master)](
https://github.com/nikolamilojica/illuminate/actions/workflows/tests.yaml)
<br>
[![Bugs](
https://sonarcloud.io/api/project_badges/measure?project=nikolamilojica_illuminate&metric=bugs)](
https://sonarcloud.io/summary/new_code?id=nikolamilojica_illuminate)
[![Code Smells](
https://sonarcloud.io/api/project_badges/measure?project=nikolamilojica_illuminate&metric=code_smells)](
https://sonarcloud.io/summary/new_code?id=nikolamilojica_illuminate)
[![Duplicated Lines (%)](
https://sonarcloud.io/api/project_badges/measure?project=nikolamilojica_illuminate&metric=duplicated_lines_density)](
https://sonarcloud.io/summary/new_code?id=nikolamilojica_illuminate)
[![Quality Gate Status](
https://sonarcloud.io/api/project_badges/measure?project=nikolamilojica_illuminate&metric=alert_status)](
https://sonarcloud.io/summary/new_code?id=nikolamilojica_illuminate)
___
<img align="left" style="margin:6px" width="200" height="200" src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Accueil_scribe_invert.png/241px-Accueil_scribe_invert.png">

> <p align="justify"><i>Data is like garbage.
> You’d better know what you are going to do with it before you
> collect it.</i></p>
> <p align="right"><i>&mdash; Mark Twain</i></p>
> <p align="justify">This code aims to be a thin,
> "batteries included", ETL framework.
> It is written using prominent Python frameworks such as
> <a href="https://alembic.sqlalchemy.org/en/latest/">Alembic</a>,
> <a href="https://click.palletsprojects.com/">Click</a>,
> <a href="https://www.tornadoweb.org/en/stable/">Tornado</a>
> and <a href="https://www.sqlalchemy.org/">SQLAlchemy</a>.
> Driver behind this project was a need for a rapid ETL
> and Scraping capabilities framework that is both development and deployment
> friendly, as well as something to return to the community.
> The whole idea is heavily influenced by
> <a href="https://www.djangoproject.com/">django</a> and
> <a href="https://scrapy.org/">Scrapy</a>.
> Tested with <a href="https://docs.pytest.org/">pytest</a> with a help of
> <a href="https://tox.wiki/en/latest/">tox</a>.</p>

## Installation
<p style="text-align: justify">Package is provided by PyPI. For this occasion,
we will create an example project, simply called "tutorial", that will use an
example from project files. In your shell, type the following:</p>

```shell
mkdir tutorial
cd tutorial
python3 -m venv venv
source venv/bin/activate
pip install beautifulsoup4 illuminated
```

> **NOTE**: Package name on PyPI is `illuminated`. Illuminate is not dependent
> on `beautifulsoup4`, but this example is.

<p style="text-align: justify">If installation is successful, you can verify
by typing:</p>

```shell
illuminate --version
```
> **NOTE**: From version `0.3.5` on, the required SQLAlchemy version is `2.0.37`
and above.

## Project Setup
<p style="text-align: justify">Once you have CLI ready to create a project
structure in the current directory, type the following:</p>

```shell
export ILLUMINATE_PGADMIN_PASSWORD=<PGADMIN_PASSWORD>
export ILLUMINATE_GRAFANA_PASSWORD=<GRAFANA_PASSWORD>
export ILLUMINATE_MAIN_DB_PASSWORD=<DB_PASSWORD>
export ILLUMINATE_MEASUREMENTS_DB_PASSWORD=<MEASUREMENTS_DB_PASSWORD>
illuminate manage project setup tutorial .
```
<p style="text-align: justify">This will create a complete project structure with all the files
and ENV vars needed to run the example ETL flow.</p>

<p style="text-align: justify">Use the provided docker-compose.yaml file and
bring the environment up.</p>

```shell
docker-compose up -d
```
<p style="text-align: justify">Once postgres and pgadmin containers are
ready, you should perform database migration by creating a revision file and
use it to upgrade the database, thus creating a table representing
<code>ExampleModel</code> provided with the project files.</p>

```shell
illuminate manage db revision
illuminate manage db upgrade
```
<p style="text-align: justify">This will create a table in the database that
will be used as a Load destination for our example.</p>

## Execution
<p style="text-align: justify">Now everything is set for Illuminate to start
observing.</p>

```shell
illuminate observe start
```

## Docker distribution
<p style="text-align: justify">Illuminate is provided as containerized
distribution as well:</p>

```shell
docker pull nikolamilojica/illuminate:latest
```
<p style="text-align: justify">To use docker distribution while inside a
project directory, type the following:</p>

```shell
docker run -it --rm --network=host \
   -e ILLUMINATE_MAIN_DB_PASSWORD=<DB_PASSWORD> \
   -e ILLUMINATE_MEASUREMENTS_DB_PASSWORD=<MEASUREMENTS_DB_PASSWORD> \
   -v $(pwd):/root/illuminate \
   nikolamilojica/illuminate illuminate observe start
```

<p style="text-align: justify">The rest of framework documentation can be
found <a href="https://nikolamilojica.github.io/illuminate/">here</a>!</p>
