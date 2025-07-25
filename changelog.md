# Change Log

## 0.4.0
* Update Docker image to use Python 3.12.
* Recursive Observer discovery.
* Observer labels and label selector.
* In settings.py, under CONCURRENCY section,
changed key "observers" to "observations".
* Update for tornado (CVE-2025-47287).
* Update for setuptools (CVE-2025-47273).
* Update for virtualenv (CVE-2024-53899).
* Update for urllib3 (CVE-2025-50182).
* Update for jinja2 (CVE-2025-27516).
* Update for requests (CVE-2024-47081).
* Update for aiohttp (CVE-2025-53643).

## 0.3.6
* Fix the bug where exception message could contain what would be
interpreted as ANSI tag, raising loguru exception in the process
and blocking async loop.
* Update for tornado (CVE-2024-52804).
* Update for aiohttp (CVE-2024-52304).
* Update for jinja2 (CVE-2024-56201).

## 0.3.5
* Switch to SQLAlchemy 2.0.
* Update for setuptools (CVE-2024-6345).

## 0.3.4
* Update for zipp (CVE-2024-5569).
* Support added for Python 3.11 and 3.12.
* Support dropped for Python 3.8.
* Update for tornado (CWE-93).
* Update for black (CVE-2024-21503).
* Update for idna (CVE-2024-3651).
* Update for Jinja2 (CVE-2024-34064).
* Update for requests (CVE-2024-35195).
* Update for urllib3 (CVE-2024-37891).
* Update for GitPython (CVE-2024-22190).
* Update for aiohttp (CVE-2024-30251).
* Update for certifi (CVE-2024-39689).
* Decouple database name from the project name with
an option. Project name will be used if no name is provided.

## 0.3.3

* Update for GitPython (CVE-2023-41040).
* Update for urllib3 (CVE-2023-45803).
* Update for aiohttp (CVE-2023-49081).
* Handle all exception generated by user code or configuration with
WARNING messages.

## 0.3.2

* Update for GitPython (CVE-2023-41040).
* Update for GitPython (CVE-2023-40590).
* Update Tornado to version 6.3.3 to fix improper integer parsing.

## 0.3.1

* Fix the bug where the logic assumes that all fixture files contain
non-relational data and tries to populate the database with malformed
JSON. Option `--fixtures` is now mandatory.
* Fix the bug in the project template where the migration script file
is incorrectly importing the Base model from the example.py file,
instead of importing it from the models package, as intended.
* Critical update for GitPython (CVE-2023-40267).

## 0.3.0

* Observation cross communication
* InfluxDBExporter

## 0.2.0

* SplashObservation
* FileObservation
* SQLObservation
* Callbacks are no loner required to return async generators. Now they can
return coroutine that will be awaited. Coroutine return object is ignored.
* Consumer/producer observation queue was hanging if exception was raised in
Observation callback method.

## 0.1.1

* Core functionalities
* HTTPObservation
* SQLExporter
