from warnings import warn

from six import add_metaclass


class ServiceBaseMeta(type):

    """Metaclass that adds the `_name` attribute to any `statsd_dep.StatsD`
    object found in the attributes.
    """

    def __new__(cls, name, bases, attrs):
        warn(
            "Use of the `ServiceBaseMeta` metaclass is no longer needed."
            " `ServiceBaseMeta` is deprecated and will be removed in a future"
            " release of `nameko-statsd`.",
            DeprecationWarning
        )

        return type.__new__(cls, name, bases, attrs)


@add_metaclass(ServiceBaseMeta)
class ServiceBase(object):
    """Service base class. """
    pass
