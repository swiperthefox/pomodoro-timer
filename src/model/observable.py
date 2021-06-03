"""Observable Class.

A subclass of Observable should define `_topics`, which is a set of available topic to subscribe.

Observers that is interested in a specific topic could register a callback using the `subscribe` method.

By defining an attribute with ObservableProperty, the changes of this attribute can be observed through
the topic 'update-xxx', where xxx is the name of the property. The callbacks will be called with two
parameters: property-value and object-value.
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
    """In a subclass of Observable, this will enable observing changes of this property.
    
    1. An `update-xxx` topic is added in available topics.
    2. Whenever the value of this property is changed, the subscribers will be notified.
    
    Usage:
        class A:
            age = ObservableProperty()
    
    """
    def __set_name__(self, owner, name):
        if issubclass(owner, Observable):
            self.update_event = 'update_' + name
            getattr(owner, '_topics').add(self.update_event)
            self.private_name = '_' + name
        else:
            raise TypeError('ObservableProperty can only be used in subclasses of Observable.')
    def __get__(self, obj, objtype = None):
        return getattr(obj, self.private_name)
        
    def __set__(self, obj, value):
        old_value = getattr(obj, self.private_name)
        if old_value == value:
            return
        setattr(obj, self.private_name, value)
        obj.notify(self.update_event, value, obj)

class UnsupportedTopicException(Exception):
    pass

class Observable:
    """This class provides basic support of observer pattern.
    
    Subclasses should define a class variable `_topic`, which is a list of subscribable topics.
    
    Three methods are defined to support the observer pattern:
    
    subscribe(topic, callback): register callback as a observer of 'topic' event.
    subscribe(topic) will create a decorator, which will register the decorated function.
    For example:
        
        @target.subscribe('change')
        def on_target_change(value):
            pass
        
    The decorator will return the original function, so it's possible to chain the decorators:
        
        @target1.subscribe('topic1')
        @target2.subscribe('topic2')
        def on_targets_change(value1=old_value1, value2=old_value2):
            pass
    
    unsubscribe(topic, callback): remove callback from the observers list.
    
    notify('topic', *args): call the topic's observers, with `args` as parameters.
    """
    # cached_property decorator makes sure that these properties will be
    # initialized to a new individual value for each instance.

    @cached_property
    def _observers(self):
        return {}
    
    _topics = set()
        
    def subscribe(self, topic, observer=None):
        """
        Attach an observer to the subject.
        """
        if self.validate_topic(topic):
            if observer is None:
                return lambda callback: self.subscribe(topic, callback)
            else:
                self._observers.setdefault(topic, set()).add(observer)
                return observer

    def unsubscribe(self, topic, observer=None):
        """
        Detach an observer from the subject.
        """
        if topic not in self._observers:
            return
        observers = self._observers[topic]
        observers.discard(observer)

    def notify(self, topic, *args):
        """
        Notify all observers about an event.
        """
        if self.validate_topic(topic):
            for obsever in self._observers.get(topic, {}):
                obsever(*args)
    
    def validate_topic(self, topic):
        if topic not in self._topics:
            error_info = (f'Class {self.__class__.__name__} does not support the required topic "{topic}"\n'
                f'Supported topics: {" ".join(self._topics)}')
            raise UnsupportedTopicException(error_info)
        return True
