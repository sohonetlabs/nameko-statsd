nameko-statsd
=============

A StatsD dependency for `nameko <http://nameko.readthedocs.org>`_, enabling
services to send stats.



Usage
-----

To use the dependency you declare it on the service and pass it the name
of the attribute (e.g. 'statsd').  Then you can use it within any of the
service methods (entrypoints, simple methods, etc.).


.. code-block:: python

    from nameko_statsd import StatsD, ServiceBase

    class Service(ServiceBase):

        statsd = StatsD('statsd-prod')

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


The `statsd.StatsClient` instance exposes a set of methods that you can
access without having to go through the client itself.  The dependency
acts as a pass-through for them.  They are: `incr`, `decr`, `gauge`,
`set`, and `timing`.

In the above code example (`get_data`), you can see how we access `incr`.

You can also decorate any method in the service with the `timer` decorator,
as shown in the example.  This allows you to time any method without having
to change its logic.


Configuration
-------------

The library expects to find the following values in the config file you
use for your service (you need one configuration block per statsd server):

.. code-block:: yaml

    STATSD:
      statsd-prod:
        host: "host-prod"
        port: 8125
        prefix: "prod-prefix"
        maxudpsize: 512
        enabled: true
      statsd-staging:
        host: "host-staging"
        port: 8125
        prefix: "staging-prefix"
        maxudpsize: 512
        enabled: false


The first four values are passed directly to `statsd.StatsClient` on
creation.  The last one, `enabled` will activate/deactivate all stats,
according to how it is set (`true`/`false`).  In this example, production
is enabled while staging is not.


The `StatsD.timer` decorator
----------------------------

At the time of writing a Nameko service, you don't have access to the
config values.  This means that when we write our service we don't have
access to the actual dependencies (they are injected later).

In order to give the users of this library the ability to decorate
methods with the `timer` decorator, we need to do a little bit of wiring
behind the scenes.  The only thing required for the end user is to write
the service class so that inherits from `nameko_statsd.ServiceBase`.

The type of `nameko_statsd.ServiceBase` is a custom metaclass that
provides the necessary wirings to any `nameko_statsd.StatsD` dependency.

You can pass any arguments to the decorator, they will be given to the
`statsd.StatsClient.timer` decorator.

So, for example:

.. code-block:: python

    class MyService(ServiceBase):

        statsd = StatsD('statsd-prod')

        @entrypoint
        @statsd.timer('my_stat', rate=5)
        def method(...):
            # method body

        @statsd.timer('another-stat')
        def another_method(...):
            # method body

is equivalent to the following:

.. code-block:: python

    class MyService(ServiceBase):

        statsd = StatsD('statsd-prod')

        @entrypoint
        def method(...):
            with self.statsd.client.timer('my_stat', rate=5):
                # method body

        def another_method(...):
            with self.statsd.client.timer('another-stat'):
                # method body


If you cannot inherit from `nameko_statsd.ServiceBase` for any reason,
all you have to do is to make sure you pass a `name` argument to any
`nameko_statsd.StatsD` dependency, the value of which has to match the
attribute name of the dependency itself, as shown in the following
example (notice the service class inherits from `object`):

.. code-block:: python

    class MyService(object):

        statsd = StatsD('statsd-prod', name='statsd')
        another_statsd = StatsD('statsd-prod2', name='another_statsd')

        @entrypoint
        @statsd.timer('my_stat', rate=5)
        def method(...):
            # method body

        @another_statsd.timer('another-stat')
        def another_method(...):
            # method body
