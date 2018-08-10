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
            'test-tcp': {
                'host': 'tcp.statsd.host',
                'port': 4321,
                'prefix': 'tcp.statsd.prefix',
                'timeout': 5,
                'enabled': True,
                'protocol': 'tcp',
            },
            'test-tcp-disabled': {
                'host': 'tcp.statsd.host.disabled',
                'port': 5432,
                'prefix': 'tcp.statsd.prefix.disabled',
                'timeout': 10,
                'enabled': False,
                'protocol': 'tcp',
            },
        }
    }
