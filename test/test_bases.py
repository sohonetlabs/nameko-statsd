import warnings

from six import add_metaclass

from nameko_statsd.bases import ServiceBaseMeta


def test_metaclass():

    @add_metaclass(ServiceBaseMeta)
    class DummyService(object):

        def some_method(self):
            pass

    assert DummyService.__name__ == 'DummyService'


def test_metaclass_deprecated(recwarn):
    warnings.simplefilter("always")

    ServiceBaseMeta('DummyService', (object,), {})

    assert len(recwarn) == 1
    warn = recwarn.pop()
    assert str(warn.message) == (
        "Use of the `ServiceBaseMeta` metaclass is no longer needed."
        " `ServiceBaseMeta` is deprecated and will be removed in a future"
        " release of `nameko-statsd`."
    )
