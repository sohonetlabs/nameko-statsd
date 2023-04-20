Nameko StatsD
=============

.. image:: https://img.shields.io/pypi/v/nameko-statsd.svg
    :target: https://pypi.org/project/nameko-statsd/

.. image:: https://img.shields.io/pypi/pyversions/nameko-statsd.svg
    :target: https://pypi.org/project/nameko-statsd/

.. image:: https://img.shields.io/pypi/format/nameko-statsd.svg
    :target: https://pypi.org/project/nameko-statsd/

.. image:: https://travis-ci.org/sohonetlabs/nameko-statsd.svg?branch=master
    :target: https://travis-ci.org/sohonetlabs/nameko-statsd

A StatsD dependency for `nameko <http://nameko.readthedocs.org>`_, enabling
services to send stats using `pystatsd <http://statsd.readthedocs.org>`_.



Usage
-----

To use the dependency you simply declare it on the service and then you
can use it within any of the service methods (entrypoints, simple methods,
etc.).


.. code-block:: python

    from nameko_statsd import StatsD

    class Service:

        statsd = StatsD('prod1')

        @entrypoint
        @statsd.timer('process_data')
        def process_data(self):
            ...

        @rpc
        def get_data(self):
            self.statsd.incr('get_data')
            ...

        def simple_method(self, value):
            self.statsd.gauge(value)
            ...

        def another_method(self, data):
            ...
            with self.statsd.timer('another_timer', rate=2):
                ...


The ``statsd.StatsClient`` instance exposes a set of methods that you can
access without having to go through the client itself.  The dependency
acts as a pass-through for them.  They are: ``incr``, ``decr``, ``gauge``,
``set``, ``timer`` and ``timing``.

In the above code example, you can see how we access ``incr``, ``gauge`` and
``timer``.

You can also decorate any method in the service with the ``timer`` decorator,
as shown in the example.  This allows you to time any method without having
to change its logic.



Configuration
-------------

The library accepts any arguments accepted by ``statsd.StatsClient`` or
``statsd.TCPStatsClient`` in the service configuration file as well as two
additional items that control the behaviour of the dependency itself
(``enabled`` and ``protocol``). You need one configuration block per different
statsd server.  For example, if we had two statsd servers, prod1 and
prod2, we could have something like this:

.. code-block:: yaml

    STATSD:
      prod1:
        enabled: true
        protocol: "udp"
        host: "host1"
        port: 8125
        prefix: "prefix-1"
        maxudpsize: 512
      prod2:
        enabled: false
        protocol: "tcp"
        host: "host2"
        port: 8125
        prefix: "prefix-2"


The ``enabled`` value will activate/deactivate all stats, according to how it
is set (``true``/``false``).  In this example, production 1 is enabled while
production 2 is not. You can set ``protocol`` to ``tcp`` (case insensitive) to
use the TCP based ``statsd.TCPStatsClient``, if ``protocol`` is omitted (or set
to ``udp``) the default UDP based ``statsd.StatsClient`` will be used. All
remaining values are passed directly to ``statsd.StatsClient`` (or
``statsd.TCPStatsClient``) on creation.


The ``StatsD.timer`` decorator
------------------------------

You can pass any arguments to the decorator, they will be given to the
``statsd.StatsClient().timer`` decorator.

So, for example:

.. code-block:: python

    class MyService:

        statsd = StatsD('prod1')

        @entrypoint
        @statsd.timer('my_stat', rate=5)
        def method(...):
            # method body

        @statsd.timer('another-stat')
        def another_method(...):
            # method body

is equivalent to the following:

.. code-block:: python

    class MyService:

        statsd = StatsD('prod1')

        @entrypoint
        def method(...):
            with self.statsd.timer('my_stat', rate=5):
                # method body

        def another_method(...):
            with self.statsd.timer('another-stat'):
                # method body


About the lazy client
---------------------

When you attach a ``nameko_statsd.StatsD`` dependency to your service, no
client is created.  Only when you use the dependency explicitly or when
you run a method that has been decorated with the ``timer`` decorator,
a client is created.

This lazy feature means you can attach as many ``nameko_statsd.StatsD``
dependencies to your service as you fancy, and no client will be created
unless it is actually used.


Nameko support
--------------

The following Nameko versions are supported: ``2.12``, ``2.13``, ``2.14``


Deprecation of the ``ServiceBase`` base class and ``name`` argument
-------------------------------------------------------------------

In previous versions of ``nameko-statsd``, the ``timer`` decorator could only
be used if the service class inherited from  ``nameko_statsd.ServiceBase`` or
if the correct ``name`` argument was passed to the ``nameko_statsd.StatsD``
dependency provider.

Since version ``0.1.1``, ``nameko_statsd.StatsD`` is able
to determine the correct attribute name when ``nameko`` binds the dependency
provider to the service. Therefore, ``name`` argument to the
``nameko_statsd.StatsD`` dependency provider, the ``nameko_statsd.ServiceBase``
base class (and the associated metaclass) have been deprecated and will be
removed in a future release.
