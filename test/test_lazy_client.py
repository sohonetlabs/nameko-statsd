from mock import Mock, call, patch
import pytest

from nameko_statsd.statsd_dep import LazyClient, Protocols


class TestLazyClient(object):

    """Test the `LazyClient` class features. """

    @pytest.fixture(autouse=True)
    def stats_client_cls(self):
        with patch('nameko_statsd.statsd_dep.StatsClient') as sc:
            yield sc

    @pytest.fixture(autouse=True)
    def stats_client_cls_tcp(self):
        with patch('nameko_statsd.statsd_dep.TCPStatsClient') as sc:
            yield sc


class TestLazyClientUDP(TestLazyClient):

    @pytest.fixture
    def stats_config(self, stats_config):
        return stats_config['STATSD']['test'].copy()

    def test_init(self, stats_client_cls, stats_client_cls_tcp, stats_config):
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
        assert stats_client_cls_tcp.call_count == 0

    @pytest.mark.parametrize('proto', ('UPD', 'upd', 'IP', 'TPC', 'tPc'))
    def test_init_invalid_protocol(
        self, stats_client_cls, stats_client_cls_tcp, stats_config, proto
    ):
        with pytest.raises(ValueError) as err:
            LazyClient(protocol=proto, **stats_config)

        assert err.match('Invalid protocol')

    def test_client_default_protocol(
        self, stats_client_cls, stats_client_cls_tcp, stats_config
    ):
        lc = LazyClient(**stats_config)

        client = lc.client  # this is a property

        assert lc.protocol is Protocols.udp

        assert stats_client_cls.call_args_list == [
            call(
                host='statsd.host',
                port=1234,
                prefix='statsd.prefix',
                maxudpsize=1024,
            )
        ]
        assert client == stats_client_cls.return_value
        assert stats_client_cls_tcp.call_count == 0

    @pytest.mark.parametrize('proto', ('udp', 'UDP', 'UdP', 'uDp'))
    def test_client_udp(
        self, stats_client_cls, stats_client_cls_tcp, stats_config, proto
    ):
        lc = LazyClient(protocol=proto, **stats_config)

        client = lc.client  # this is a property

        assert lc.protocol is Protocols.udp

        assert stats_client_cls.call_args_list == [
            call(
                host='statsd.host',
                port=1234,
                prefix='statsd.prefix',
                maxudpsize=1024,
            )
        ]
        assert client == stats_client_cls.return_value
        assert stats_client_cls_tcp.call_count == 0


class TestLazyClientTCP(TestLazyClient):

    @pytest.fixture
    def stats_config(self, stats_config):
        return stats_config['STATSD']['test-tcp'].copy()

    def test_init(
        self, stats_client_cls, stats_client_cls_tcp, stats_config
    ):
        lc = LazyClient(**stats_config)

        assert lc.config == dict(
            host='tcp.statsd.host',
            port=4321,
            prefix='tcp.statsd.prefix',
            timeout=5,
        )
        assert lc.enabled
        assert lc._client is None
        assert stats_client_cls.call_count == 0
        assert stats_client_cls_tcp.call_count == 0

    @pytest.mark.parametrize('proto', ('tcp', 'TCP', 'TcP', 'tCp'))
    def test_client(
        self, stats_client_cls, stats_client_cls_tcp, stats_config, proto
    ):
        del stats_config['protocol']
        lc = LazyClient(protocol=proto, **stats_config)

        client = lc.client  # this is a property

        assert lc.protocol is Protocols.tcp

        assert stats_client_cls_tcp.call_args_list == [
            call(
                host='tcp.statsd.host',
                port=4321,
                prefix='tcp.statsd.prefix',
                timeout=5,
            )
        ]
        assert client == stats_client_cls_tcp.return_value
        assert stats_client_cls.call_count == 0


class TestStatMethods(TestLazyClient):

    @pytest.fixture(params=['test', 'test-tcp'])
    def stats_config(self, request, stats_config):
        return stats_config['STATSD'][request.param].copy()

    @pytest.mark.parametrize('method', [
        'incr', 'decr', 'gauge', 'set', 'timing'
    ])
    def test_passthrough_methods(self, method, stats_config):
        lc = LazyClient(**stats_config)

        delegate = getattr(lc, method)

        # make the call
        delegate(1, 2, 3, 'Darth Vader', obi_wan='Kenobi')

        # verify it's a passthrough
        assert getattr(lc.client, method).call_args_list == [
            call(1, 2, 3, 'Darth Vader', obi_wan='Kenobi')
        ]

    @pytest.mark.parametrize('method', [
        'incr', 'decr', 'gauge', 'set', 'timing'
    ])
    def test_passthrough_disabled(
        self, method, stats_config
    ):
        stats_config['enabled'] = False
        lc = LazyClient(**stats_config)

        delegate = getattr(lc, method)

        # make the call
        delegate(1, 2, 3, 'Darth Vader', obi_wan='Kenobi')

        assert getattr(lc.client, method).call_args_list == []

    def test_getattr(self, stats_config):
        lc = LazyClient(**stats_config)

        with pytest.raises(AttributeError) as exc_info:
            lc.missing_method()

        assert exc_info.match(
            "'LazyClient' object has no attribute 'missing_method'"
        )

    def test_timer_contextmanager_enabled(
        self, stats_client_cls, stats_config
    ):
        lc = LazyClient(**stats_config)

        with lc.timer('stat', rate=2) as timer:
            pass

        assert timer is lc.client.timer.return_value.__enter__.return_value
        assert lc.client.timer.call_args_list == [call('stat', rate=2)]

    def test_timer_contextmanager_disabled(
        self, stats_client_cls, stats_config
    ):
        stats_config['enabled'] = False
        lc = LazyClient(**stats_config)

        with lc.timer('stat', rate=2) as timer:
            pass

        assert isinstance(timer, Mock)
        assert lc.client.timer.call_args_list == []
