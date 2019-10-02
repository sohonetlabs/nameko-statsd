from enum import Enum
from functools import wraps, partial
from mock import MagicMock
from warnings import warn

from nameko.extensions import DependencyProvider
from statsd import StatsClient, TCPStatsClient


class Protocols(Enum):
    tcp = 'tcp'
    udp = 'udp'


class LazyClient(object):

    """Provide an interface to `StatsClient` with a lazy client creation.
    """

    def __init__(self, **config):
        self.config = config
        self.enabled = config.pop('enabled')
        self._client = None

        protocol = self.config.pop('protocol', Protocols.udp.name)

        try:
            self.protocol = getattr(Protocols, protocol.lower())
        except AttributeError:
            raise ValueError(
                'Invalid protocol: {}'.format(protocol)
            )

    @property
    def client(self):
        if self._client is None:
            if self.protocol is Protocols.udp:
                self._client = StatsClient(**self.config)
            else:   # self.protocol is Protocols.tcp
                self._client = TCPStatsClient(**self.config)

        return self._client

    def __getattr__(self, name):
        if name in ('incr', 'decr', 'gauge', 'set', 'timing'):
            return partial(self._passthrough, name)
        else:
            message = "'{cls}' object has no attribute '{attr}'".format(
                cls=self.__class__.__name__, attr=name
            )
            raise AttributeError(message)

    def _passthrough(self, name, *args, **kwargs):
        if self.enabled:
            return getattr(self.client, name)(*args, **kwargs)

    def timer(self, *args, **kwargs):
        if self.enabled:
            return self.client.timer(*args, **kwargs)
        else:
            return MagicMock()

    def pipeline(self, *args, **kwargs):
        if self.enabled:
            return self.client.pipeline(*args, **kwargs)
        else:
            return MagicMock()


class StatsD(DependencyProvider):

    def __init__(self, key, name=None, *args, **kwargs):
        """
        Args:
            key (str): The key under the `STATSD` config dictionary.
            name (str): The name associated to the instance.
        """
        self._key = key

        if name is not None:
            warn(
                "The `name` argument to `StatsD` is no longer needed and has"
                " been deprecated.",
                DeprecationWarning
            )

        super(StatsD, self).__init__(*args, **kwargs)

    def get_dependency(self, worker_ctx):
        return LazyClient(**self.config)

    def setup(self):
        self.config = self.get_config()
        return super(StatsD, self).setup()

    def get_config(self):
        return self.container.config['STATSD'][self._key]

    def timer(self, *targs, **tkwargs):
        """Decorate a nameko service method.

        It can be applied to any instance method in a nameko service class,
        even to RPC or HTTP entrypoints.  If `dependency.enabled` is `False`
        this decorator is equivalent to a no-op.

        Args:
            *targs: Positional arguments to be given to `StatsClient.timer()`.
            *tkwargs: Keyword arguments to be given to `StatsClient.timer()`.

        Decorating a service like this:

        .. code-block:: python

            class MyService:

                statsd = StatsD('config_key')

                @rpc (or @http or even nothing)
                @statsd.timer('my_stat', rate=5)
                def method(...):
                    # method body

        is equivalent to the following:

        .. code-block:: python

            class MyService:

                statsd = StatsD('config_key')

                @rpc (or @http or even nothing)
                def method(...):
                    with self.statsd.client.timer('my_stat', rate=5):
                        # method body

        """
        def decorator(method):

            @wraps(method)
            def wrapper(svc, *args, **kwargs):
                # self.attr_name starts as None, then is set to the name of
                # the attribute when bind is called. Until then, the decorator
                # does nothing
                if self.attr_name is None:
                    return method(svc, *args, **kwargs)

                dependency = getattr(svc, self.attr_name)

                if dependency.enabled:
                    with dependency.client.timer(*targs, **tkwargs):
                        res = method(svc, *args, **kwargs)
                else:
                    res = method(svc, *args, **kwargs)

                return res

            return wrapper

        return decorator
