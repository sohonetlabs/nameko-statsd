from copy import deepcopy
from mock import call, Mock, patch

import pytest
from nameko.testing.services import dummy, entrypoint_hook

from nameko_statsd.statsd_dep import StatsD, LazyClient


class TestStatsD(object):

    @pytest.fixture
    def lazy_client_cls(self):
        with patch('nameko_statsd.statsd_dep.LazyClient') as lc:
            yield lc

    def test_get_dependency(self, lazy_client_cls, stats_config):
        statsd = StatsD('statsd')
        statsd.container = Mock()
        statsd.container.config = stats_config
        statsd.setup()

        worker_ctx = Mock()

        dep = statsd.get_dependency(worker_ctx)

        assert lazy_client_cls.call_args_list == [
            call(
                host='statsd.host',
                port=1234,
                prefix='statsd.prefix',
                maxudpsize=1024,
                enabled=True,
            )
        ]
        assert dep == lazy_client_cls.return_value


class DummyService(object):

    """Fake Service to test the `StatsD.timer` decorator. """

    name = 'test_service'

    sd = StatsD('sd')

    @dummy
    @sd.timer('nice-stat', rate=3)
    def method(self, *args, **kwargs):
        sentinel = Mock()
        sentinel(*args, **kwargs)
        return sentinel


class TestTimer(object):

    @pytest.fixture
    def config(self, stats_config):
        return stats_config.copy()

    @pytest.fixture
    def stats_client_cls(self):
        with patch('nameko_statsd.statsd_dep.StatsClient') as sc:
            yield sc

    def test_enabled(self, container_factory, config, stats_client_cls):
        container = container_factory(DummyService, config)
        container.start()

        with entrypoint_hook(container, 'method') as method:
            sentinel = method(3, 1, 4, name='pi')

        client = stats_client_cls.return_value

        assert client.timer.call_args_list == [call('nice-stat', rate=3)]
        assert sentinel.call_args_list == [call(3, 1, 4, name='pi')]

    def test_disabled(self, container_factory, config, stats_client_cls):
        config['STATSD']['enabled'] = False
        container = container_factory(DummyService, config)
        container.start()

        with entrypoint_hook(container, 'method') as method:
            sentinel = method(3, 1, 4, name='pi')

        client = stats_client_cls.return_value

        assert stats_client_cls.call_args_list == []
        assert client.timer.call_args_list == []
        assert sentinel.call_args_list == [call(3, 1, 4, name='pi')]


class TestLazyClient(object):

    @pytest.fixture
    def stats_config(self, stats_config):
        return stats_config['STATSD']

    @pytest.fixture
    def stats_client_cls(self):
        with patch('nameko_statsd.statsd_dep.StatsClient') as sc:
            yield sc

    def test_init(self, stats_client_cls, stats_config):
        lc = LazyClient(**stats_config)

        assert lc.config == dict(
            host='statsd.host',
            port=1234,
            prefix='statsd.prefix',
            maxudpsize=1024,
        )
        assert lc.enabled
        assert lc._client is None
        assert stats_client_cls.call_count == 0

    def test_client(self, stats_client_cls, stats_config):
        lc = LazyClient(**stats_config)

        client = lc.client  # this is a property

        assert stats_client_cls.call_args_list == [
            call(
                host='statsd.host',
                port=1234,
                prefix='statsd.prefix',
                maxudpsize=1024,
            )
        ]
        assert client == stats_client_cls.return_value

    @pytest.mark.parametrize('method', [
        'incr', 'decr', 'gauge', 'set', 'timing'
    ])
    def test_passthrough_methods(self, method, stats_client_cls, stats_config):
        lc = LazyClient(**stats_config)

        args = (1, 2, 3, 'a')
        kwargs = dict(a=1, b='2')

        delegate = getattr(lc, method)

        # make the call
        delegate(*deepcopy(args), **deepcopy(kwargs))

        # verify it's a passthrough
        assert getattr(lc.client, method).call_args_list == [
            call(*args, **kwargs)
        ]

    @pytest.mark.parametrize('method', [
        'incr', 'decr', 'gauge', 'set', 'timing'
    ])
    def test_passthrough_disabled(
        self, method, stats_client_cls, stats_config
    ):
        stats_config['enabled'] = False
        lc = LazyClient(**stats_config)

        args = (1, 2, 3, 'a')
        kwargs = dict(a=1, b='2')

        delegate = getattr(lc, method)

        # make the call
        delegate(*deepcopy(args), **deepcopy(kwargs))

        assert getattr(lc.client, method).call_args_list == []

    def test_getattr(self, stats_client_cls, stats_config):
        lc = LazyClient(**stats_config)

        with pytest.raises(AttributeError):
            lc.missing_method()
