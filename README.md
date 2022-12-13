# Illuminate

[![Code Style: Black](
https://img.shields.io/badge/code%20style-black-000000.svg)](
https://github.com/psf/black)
[![Coveralls Coverage](
https://coveralls.io/repos/github/nikolamilojica/illuminate/badge.svg?branch=develop&t=YU1NaL)](
https://coveralls.io/github/nikolamilojica/illuminate?branch=develop)
[![GitHub Actions - Tests Workflow](
https://github.com/nikolamilojica/illuminate/actions/workflows/tests.yaml/badge.svg?branch=develop)](
https://github.com/nikolamilojica/illuminate/actions/workflows/tests.yaml)
___
<img align="left" style="margin:8px;" src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/Accueil_scribe_invert.png/241px-Accueil_scribe_invert.png">

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
pip install illuminated
```

> **NOTE**: Package name on PyPI is illuminated.

<p style="text-align: justify">If installation is successful, you can verify
by typing:</p>

```shell
illuminate --version
```
## Project Setup
<p style="text-align: justify">Once you have CLI ready to create a project
structure in the current directory, type the following:</p>

```shell
export ILLUMINATE_PGADMIN_PASSWORD=<PASSWORD>
export ILLUMINATE_MAIN_DB_PASSWORD=<PASSWORD>
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
   -e ILLUMINATE_MAIN_DB_PASSWORD=illuminate \
   -v .:/root/illuminate \
   nikolamilojica/illuminate illuminate observe start
```
