Release Notes
=============

Here you can see the full list of changes between
nameko-statsd versions, where semantic versioning is used:
*major.minor.patch*.

Backwards-compatible changes increment the minor version number only.


Version 0.1.2
-------------
* Only install enum backport when needed

Version 0.1.1
-------------

* Deprecate the `ServiceBaseMeta` metaclass and the `name` argument to the
  `StatsD` dependency provider.
* Add support for pipeline when disabled
* Test on older Nameko versions (back to 2.7) and against pre-release versions of
  dependencies.
* Test on Python 3.8

Version 0.1.0
-------------

Release 2019-03-21

* Add support for Python 3.7 (#10)
* Add Nameko ``2.11`` and ``2.12`` support (#10)
* Switch to semantic versioning (#10)


Version 0.0.6
-------------

Released 2018-11-14

* Fix a bug in the `ServiceBaseMeta` metaclass which caused classes to have the
  wrong name.


Version 0.0.5
-------------

Released 2018-08-10

* Enable use of TCP instead of UDP.

Version 0.0.4
-------------

Released 2018-07-25

* Enable use of `timer` as context manager, respecting the `enabled` setting.


Version 0.0.3
-------------

Released 2017-06-15

* Relax requirements.


Version 0.0.2
-------------

Released 2017-06-15

* Amend license.


Version 0.0.1
-------------

Released 2017-06-15

* Initial release.
