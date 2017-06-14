from mock import call, patch
import pytest

from nameko_statsd.statsd_dep import LazyClient


class TestLazyClient(object):

    """Test the `LazyClient` class features. """

    @pytest.fixture
    def stats_config(self, stats_config):
        return stats_config['STATSD']['test'].copy()

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
        self, method, stats_client_cls, stats_config
    ):
        stats_config['enabled'] = False
        lc = LazyClient(**stats_config)

        delegate = getattr(lc, method)

        # make the call
        delegate(1, 2, 3, 'Darth Vader', obi_wan='Kenobi')

        assert getattr(lc.client, method).call_args_list == []

    def test_getattr(self, stats_client_cls, stats_config):
        lc = LazyClient(**stats_config)

        with pytest.raises(AttributeError):
            lc.missing_method()
