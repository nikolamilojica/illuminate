# Change Log

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
JSON. Option --fixtures is now mandatory.
* Fix the bug in the project template where the migration script file
is incorrectly importing the Base model from the example.py file,
instead of importing it from the models package, as intended.
* Critical update for GitPython (CVE-2023-40267).

## 0.3.0

* Observation cross communication
* InfluxDBExporter

## 0.2.0

Features:
* SplashObservation
* FileObservation
* SQLObservation
* Callbacks are no loner required to return async generators. Now they can
return coroutine that will be awaited. Coroutine return object is ignored.

Fixes:
* Consumer/producer observation queue was hanging if exception was raised in
Observation callback method. [#95](https://github.com/nikolamilojica/illuminate/pull/95)

## 0.1.1

Features:
* Core functionalities
* HTTPObservation
* SQLExporter
