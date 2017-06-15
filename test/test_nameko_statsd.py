from mock import call, Mock, patch
import pytest
from nameko.testing.services import dummy, entrypoint_hook

from nameko_statsd.statsd_dep import StatsD
from nameko_statsd.bases import ServiceBase


class TestStatsD(object):

    """Test the dependency provider mechanics. """

    @pytest.fixture
    def lazy_client_cls(self):
        with patch('nameko_statsd.statsd_dep.LazyClient') as lc:
            yield lc

    def test_get_dependency(self, lazy_client_cls, stats_config):
        statsd = StatsD('test')
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


class DummyService(ServiceBase):

    """Fake Service to test the `StatsD.timer` decorator. """

    name = 'dummy_service'

    statsd = StatsD('test')

    @dummy
    @statsd.timer('nice-stat', rate=3)
    def method(self, *args, **kwargs):
        sentinel = Mock()
        sentinel(*args, **kwargs)
        return sentinel


class DummyServiceDisabled(ServiceBase):

    """Fake Service to test the `StatsD.timer` decorator when disabled. """

    name = 'dummy_service'

    statsd = StatsD('test-disabled')

    @dummy
    @statsd.timer('disabled-nice-stat')
    def method(self, *args, **kwargs):
        sentinel = Mock()
        sentinel(*args, **kwargs)
        return sentinel


class DummyServiceManual(object):

    """Fake Service to test the `StatsD.timer` decorator without metaclass. """

    name = 'dummy_service'

    statsd = StatsD('test', name='statsd')

    @dummy
    @statsd.timer('nice-stat', rate=3)
    def method(self, *args, **kwargs):
        sentinel = Mock()
        sentinel(*args, **kwargs)
        return sentinel


class TestTimer(object):

    """Test the `StatsD.timer` decorator. """

    @pytest.fixture
    def config(self, stats_config):
        return stats_config.copy()

    @pytest.fixture
    def stats_client_cls(self):
        with patch('nameko_statsd.statsd_dep.StatsClient') as sc:
            yield sc

    def test_enabled_with_metaclass(
        self, container_factory, config, stats_client_cls
    ):
        container = container_factory(DummyService, config)
        container.start()

        with entrypoint_hook(container, 'method') as method:
            sentinel = method(3, 1, 4, name='pi')

        client = stats_client_cls.return_value

        assert client.timer.call_args_list == [call('nice-stat', rate=3)]
        assert sentinel.call_args_list == [call(3, 1, 4, name='pi')]

    def test_enabled_no_metaclass(
        self, container_factory, config, stats_client_cls
    ):
        container = container_factory(DummyServiceManual, config)
        container.start()

        with entrypoint_hook(container, 'method') as method:
            sentinel = method(3, 1, 4, name='pi')

        client = stats_client_cls.return_value

        assert client.timer.call_args_list == [call('nice-stat', rate=3)]
        assert sentinel.call_args_list == [call(3, 1, 4, name='pi')]

    def test_disabled(self, container_factory, config, stats_client_cls):
        container = container_factory(DummyServiceDisabled, config)
        container.start()

        with entrypoint_hook(container, 'method') as method:
            sentinel = method(3, 1, 4, name='pi')

        client = stats_client_cls.return_value

        assert stats_client_cls.call_args_list == []
        assert client.timer.call_args_list == []
        assert sentinel.call_args_list == [call(3, 1, 4, name='pi')]
