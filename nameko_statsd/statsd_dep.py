from functools import wraps, partial

from nameko.extensions import DependencyProvider
from statsd import StatsClient


class LazyClient(object):

    """Provide an interface to `StatsClient` with a lazy client creation.
    """

    def __init__(self, **config):
        self.config = dict(
            host=config['host'],
            port=config['port'],
            prefix=config['prefix'],
            maxudpsize=config['maxudpsize'],
        )
        self.enabled = config['enabled']
        self._client = None

    @property
    def client(self):
        if self._client is None:
            self._client = StatsClient(**self.config)
        return self._client

    def __getattr__(self, name):
        if name in ('incr', 'decr', 'gauge', 'set', 'timing'):
            return partial(self._passthrough, name)
        else:
            return super(LazyClient, self).__getattr__(name)

    def _passthrough(self, name, *args, **kwargs):
        if self.enabled:
            return getattr(self.client, name)(*args, **kwargs)


class StatsD(DependencyProvider):

    def __init__(self, name, *args, **kwargs):
        self.__name = name
        super(StatsD, self).__init__(*args, **kwargs)

    def get_dependency(self, worker_ctx):
        return LazyClient(**self.config)

    def setup(self):
        self.config = self.get_config()
        return super(StatsD, self).setup()

    def get_config(self):
        config = self.container.config['STATSD']
        return dict(
            host=config['host'],
            port=config['port'],
            prefix=config['prefix'],
            maxudpsize=config['maxudpsize'],
            enabled=config['enabled']
        )

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

        """
        def decorator(method):

            @wraps(method)
            def wrapper(svc, *args, **kwargs):
                dependency = getattr(svc, self.__name)

                if dependency.enabled:
                    with dependency.client.timer(*targs, **tkwargs):
                        res = method(svc, *args, **kwargs)
                else:
                    res = method(svc, *args, **kwargs)

                return res

            return wrapper

        return decorator
