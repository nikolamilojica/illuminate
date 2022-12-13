## Disclaimer
<p style="text-align: justify">Version 0.X will be a playground where
functionalities are added, until there is enough knowledge for better API.
Even now some inconsistencies are obvious. For example, all
<code>Observers</code> and <code>Adapters</code> are picked up by
<code>Assistant</code> class but models are specified in
<code>settings.py</code> module. This said, you are warned, version 0.X
comes with no guarantees. Your projects will be completely broken when
version 1.X hits the shelves.</p>

## Future releases
<p style="text-align: justify">The next few minor releases would focus on
additional <code>Exporter</code> and <code>Observation</code> classes.
Everything async is a good candidate if it used in ETL. It should also focus on
integration with cloud service providers, to include their services as
<code>Exporter</code> and <code>Observation</code> classes</p>

<p style="text-align: justify">Small list of features would include:</p>

- [ ] `Exporter` Classes
    * [ ] AWSS3Exporter - AWS S3 cloud service integration exporter
    * [ ] FileExporter - File exporter
    * [ ] HTTPExporter - HTTP exporter
    * [ ] NoSQLExporter - NoSQL database exporter
    * [ ] SplashExporter - Web 2.0 proxy js renderer exporter
- [ ] `Observation` Classes
    * [ ] AWSS3Observation - AWS S3 cloud service integration observation
    * [ ] FileObservation - File observation
    * [ ] NoSQLObservation - NoSQL database observation
    * [ ] SplashObservation - Web 2.0 proxy js renderer observation
    * [ ] SQLObservation - SQL observation

## Future needs you!
<p style="text-align: justify">Consider becoming a contributor.</p>
