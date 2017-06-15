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

    def __init__(self, key, name=None, *args, **kwargs):
        """
        Args:
            key (str): The key under the `STATSD` config dictionary.
            name (str): The name associated to the instance.
        """
        self._key = key
        self._name = name or ''
        super(StatsD, self).__init__(*args, **kwargs)

    def get_dependency(self, worker_ctx):
        return LazyClient(**self.config)

    def setup(self):
        self.config = self.get_config()
        return super(StatsD, self).setup()

    def get_config(self):
        return self.container.config['STATSD'][self._key]

    def timer(self, *targs, **tkwargs):

        def decorator(method):

            @wraps(method)
            def wrapper(svc, *args, **kwargs):
                dependency = getattr(svc, self._name)

                if dependency.enabled:
                    with dependency.client.timer(*targs, **tkwargs):
                        res = method(svc, *args, **kwargs)
                else:
                    res = method(svc, *args, **kwargs)

                return res

            return wrapper

        return decorator
