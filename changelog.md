# Change Log

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
