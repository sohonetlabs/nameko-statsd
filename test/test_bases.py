from six import add_metaclass

from nameko_statsd.bases import ServiceBaseMeta


def test_metaclass():

    @add_metaclass(ServiceBaseMeta)
    class DummyService(object):

        def some_method(self):
            pass

    assert DummyService.__name__ == 'DummyService'
