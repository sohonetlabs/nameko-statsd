import pytest


@pytest.fixture
def stats_config():
    return {
        'STATSD': {
            'test': {
                'host': 'statsd.host',
                'port': 1234,
                'prefix': 'statsd.prefix',
                'maxudpsize': 1024,
                'enabled': True,
            },
            'test-disabled': {
                'host': 'statsd.host.disabled',
                'port': 2345,
                'prefix': 'statsd.prefix.disabled',
                'maxudpsize': 128,
                'enabled': False,
            },
        }
    }
