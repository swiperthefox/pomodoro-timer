"""
Observer pattern.
"""
# cached_property implementation from Werkzeug project (see https://stackoverflow.com/questions/12084445/python-change-a-property-getter-after-the-fact)
# python 3.9 provide it in functools.

_missing = object()

class cached_property(object):
    """A decorator that converts a function into a lazy property.  The
    function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access
    the value::

        class Foo(object):

            @cached_property
            def foo(self):
                # calculate something important here
                return 42

    The class has to have a `__dict__` in order for this property to
    work.
    """

    # implementation detail: this property is implemented as non-data
    # descriptor.  non-data descriptors are only invoked if there is
    # no entry with the same name in the instance's __dict__.
    # this allows us to completely get rid of the access function call
    # overhead.  If one choses to invoke __get__ by hand the property
    # will still work as expected because the lookup logic is replicated
    # in __get__ for manual invocation.

    def __init__(self, func, name=None, doc=None):
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __get__(self, obj, type=None):
        if obj is None:
            return self
        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value

#from functools import cached_property
class Observable:
    """
    The Subject interface declares a set of methods for managing subscribers.
    """
    @cached_property
    def _observer_id(self):
        return 0

    @cached_property
    def _observers(self):
        return {}
    
    def attach(self, observer) -> None:
        """
        Attach an observer to the subject.
        """
        self._observers[self._observer_id] = observer
        self._observer_id += 1

    def detach(self, *, oid=None, observer=None):
        """
        Detach an observer from the subject.
        """
        if oid in self._observers:
            self._observers.pop(oid)
        elif observer is not None:
            keys = list(self._observers.keys())
            for k in keys:
                if self._observers[k] == observer:
                    self._observers.pop(k)

    def notify(self):
        """
        Notify all observers about an event.
        """
        for obsever in self._observers.values():
            obsever(self)
