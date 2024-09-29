import sys
import typing
import weakref
import types


if typing.TYPE_CHECKING:
    from radium.nodegraph.factory.prototypes import ParameterPrototype

ChangeCallback = typing.Callable[["Parameter", typing.Any, typing.Any], None]


def callable_weak_ref(callback: typing.Callable):

    # if were passed a lambda function we need to pass it right back to the

    if not callable(callback):
        raise TypeError("callback must be callable")

    elif isinstance(callback, types.FunctionType):
        return weakref.ref(callback)

    elif isinstance(callback, types.MethodType) and callback.__self__ is not None:
        return weakref.WeakMethod(callback)
    elif isinstance(callback, types.MethodType) and callback.__self__ is None:
        raise TypeError(
            "callback must be a bound method, a function, or a callable class"
        )
    else:
        # otherwise it's a callable class.
        return weakref.ref(callback)


CallbackType = typing.TypeVar("CallbackType", bound=typing.Callable)


class Observable(typing.Generic[CallbackType]):
    """
    A light-weight signal stand-in.

    The API of this class is deliberately distinct from Signals so that they are clearly distinguishable while in use.
    """

    def __init__(self):
        self.__observers = []

    def publish(self, *args, **kwargs):
        for is_wrapped, wrapped_callback in self.__observers:
            if is_wrapped:
                callback = wrapped_callback()
            else:
                callback = wrapped_callback

            callback(*args, **kwargs)

    def subscribe(self, callback: CallbackType):
        # if the current object only has 2 active references then it is presumed to be a lambda function and we will
        # reference it directly so as not to let it become garbage collected.
        if sys.getrefcount(callback) == 2:
            self.__observers.append((False, callback))
        else:
            self.__observers.append((True, callable_weak_ref(callback)))

    def unSubscribe(self, callback: CallbackType):
        self.__observers = [o for o in self.__observers if o() is not callback]


class ParameterDataDict(typing.TypedDict):
    name: str
    datatype: str
    value: typing.Any
    default: typing.Any
    metadata: typing.Dict[str, typing.Any]


class Parameter:
    """
    A parameter is a container for an observable value
    """

    def __init__(self, name, datatype, value, default, **metadata):
        self.__name = name
        self.__datatype = datatype
        self.__default = default
        self.__metadata = metadata
        self.__value = value
        self.valueChanged: Observable[ChangeCallback] = Observable()

    def name(self):
        return self.__name

    def datatype(self):
        return self.__datatype

    def default(self):
        return self.__default

    def reset(self):
        self.setValue(self.__default)

    def value(self):
        return self.__value

    def metadata(self):
        return self.__metadata

    def setValue(self, value):
        previous = self.value
        self.__value = value
        self.valueChanged.publish(self, previous, value)

    def loadDict(self, data: ParameterDataDict):
        self.__name = data["name"]
        self.__datatype = data["datatype"]
        self.__value = data["value"]
        self.__default = data["default"]

    def dumpDict(self):
        return ParameterDataDict(
            name=self.__name,
            datatype=self.__datatype,
            value=self.__value,
            default=self.__default,
            metadata=self.__metadata.copy(),
        )
