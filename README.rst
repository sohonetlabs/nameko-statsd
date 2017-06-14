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

    from nameko_statsd import StatsD

    class Service(object):

        statsd = StatsD('statsd')

        @entrypoint
        @statsd.timer('process_data')
        def process_data(self):
            ...

        @rpc
        def get_data(self):
            self.statsd.incr('get_data')
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
use for your service:

.. code-block:: yaml

    STATSD:
      host: "host"
      port: 8125
      prefix: "your-prefix"
      maxudpsize: 512
      enabled: true


The first four values are passed directly to `statsd.StatsClient` on
creation.  The last one, `enabled` will activate/deactivate all stats,
according to how it is set (`true`/`false`).


The `StatsD.timer` decorator
----------------------------

Nameko gives you access to the config values when the worker is being
prepared for an execution.  This means that when we write our service
we don't have access to the actual dependencies (they are injected later).

In order to give the users of this library the ability to decorate
methods with the `timer` decorator, we need to do a little bit of wiring
behind the scenes.  The only thing required for the end user is to pass
the string representation of the dependency name to the `StatsD`
constructor, as shown in the above example.

You can pass any arguments to the decorator, they will be given to the
`statsd.StatsClient.timer` decorator.

So, for example:

.. code-block:: python

    class MyService:

        statsd = StatsD('statsd')

        @rpc (or @http or even nothing)
        @statsd.timer('my_stat', rate=5)
        def method(...):
            # method body

is equivalent to the following:

.. code-block:: python

    class MyService:

        statsd = StatsD('statsd')

        @rpc (or @http or even nothing)
        def method(...):
            with self.statsd.client.timer('my_stat', rate=5):
                # method body