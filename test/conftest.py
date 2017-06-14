import pytest


@pytest.fixture
def stats_config():
    return {
        'STATSD': {
            'host': 'statsd.host',
            'port': 1234,
            'prefix': 'statsd.prefix',
            'maxudpsize': 1024,
            'enabled': True,
        }
    }
