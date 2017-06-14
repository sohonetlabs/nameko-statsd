from six import add_metaclass

from .statsd_dep import StatsD


class ServiceBaseMeta(type):

    """Metaclass that adds the `_name` attribute to any `statsd_dep.StatsD`
    object found in the attributes.
    """

    def __new__(cls, name, bases, attrs):

        for name, obj in attrs.items():
            if isinstance(obj, StatsD):
                obj._name = name

        return type.__new__(cls, name, bases, attrs)


@add_metaclass(ServiceBaseMeta)
class ServiceBase(object):
    """Service base class. """
