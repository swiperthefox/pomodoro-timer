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

class ObservableProperty:
    """In an subclass of Observable, this will add an 'update_***' topic for the property."""
    def __set_name__(self, owner, name):
        if issubclass(owner, Observable):
            self.update_event = 'update_' + name
            getattr(owner, 'subscribable_topics').add(self.update_event)
            self.private_name = '_' + name
            print(f"binding property {name}")
        else:
            raise TypeError('ObservableProperty can only be used in subclasses of Observable.')
    def __get__(self, obj, objtype = None):
        return getattr(obj, self.private_name)
        
    def __set__(self, obj, value):
        setattr(obj, self.private_name, value)
        # notify listeners
        obj.notify(self.update_event, value)

class UnsupportedTopicException(Exception):
    pass

class Observable:
    """
    The interface declares a set of methods for managing subscribers.
    """
    # cached_property decorator makes sure that these properties will be
    # initialized to a new individual value for each instance.
    @cached_property
    def _observer_id(self):
        return 0

    @cached_property
    def _observers(self):
        return {}
    
    subscribable_topics = set()
        
    def subscribe(self, topic, observer) -> None:
        """
        Attach an observer to the subject.
        """
        if self.check_topic(topic):
            self._observers.setdefault(topic, {})[self._observer_id] = observer
            self._observer_id += 1

    def unsubscribe(self, topic, *, oid=None, observer=None):
        """
        Detach an observer from the subject.
        """
        if topic not in self._observers:
            return
        observers = self._observers[topic]
        if oid in observers:
            observers.pop(oid)
        elif observer is not None:
            keys = list(observers.keys())
            for k in keys:
                if observers[k] == observer:
                    observers.pop(k)

    def notify(self, topic, *args):
        """
        Notify all observers about an event.
        """
        if self.check_topic(topic):
            for obsever in self._observers.get(topic, {}).values():
                obsever(*args)
    
    def check_topic(self, topic):
        if topic not in self.subscribable_topics:
            error_info = (f'Class {self.__class__.__name__} does not support the required topic "{topic}"\n'
                f'Supported topics: {" ".join(self.subscribable_topics)}')
            raise UnsupportedTopicException(error_info)
        return True
