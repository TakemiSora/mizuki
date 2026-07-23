from datetime import datetime
from typing import Any, Literal, Protocol, cast, overload
from collections.abc import Callable, Coroutine, Iterable


class Missing:
    __slots__ = ()

    def __bool__(self) -> bool:
        return False


_MISSING: Any = Missing()

type CoroFunc = Callable[..., Coroutine[Any, Any, Any]]
type CoroDecorator = Callable[[CoroFunc], CoroFunc]
type JSONPayload = Any


class SupportsToDict[T](Protocol):
    def _to_dict(self) -> T: ...


def assign_val[T](obj: T, check_against: Any = _MISSING, /, **kwargs: Any) -> T:
    for key, val in kwargs.items():
        if val is not check_against:
            setattr(obj, key, val)
    return obj


def mtd[T](obj: SupportsToDict[T] | Missing | None) -> T | None:
    if obj is not None and not isinstance(obj, Missing):
        return obj._to_dict()


@overload
def maybe_iter[IterableType, ReturnType](
    obj: Iterable[IterableType] | Missing,
    method: Callable[[IterableType], ReturnType] = mtd,
    enumerate_iter: Literal[False] = False,
    check_against: tuple[Any, ...] = (_MISSING,),
) -> list[ReturnType] | Missing: ...


@overload
def maybe_iter[IterableType, ReturnType](
    obj: Iterable[IterableType] | Missing,
    method: Callable[[int, IterableType], ReturnType],
    enumerate_iter: Literal[True],
    check_against: tuple[Any, ...] = (_MISSING,),
) -> list[ReturnType] | Missing: ...


def maybe_iter[IterableType, ReturnType](
    obj: Iterable[IterableType] | Missing,
    method: Callable[[IterableType], ReturnType]
    | Callable[[int, IterableType], ReturnType] = mtd,
    enumerate_iter: bool = False,
    check_against: tuple[Any, ...] = (_MISSING,),
) -> list[ReturnType] | Missing:
    if obj in check_against or isinstance(obj, Missing):
        return cast(Missing, obj)

    if enumerate_iter:
        casted_method = cast(Callable[[int, IterableType], ReturnType], method)
        return [casted_method(i, item) for i, item in enumerate(obj)]

    casted_method = cast(Callable[[IterableType], ReturnType], method)
    return [casted_method(item) for item in obj]


def assign_val_dict[T](d: T, check_against: Any = None, /, **kwargs: Any) -> T:
    for key, val in kwargs.items():
        if val is not check_against:
            d[key] = val  # type: ignore
    return d


def sint(txt: str | None) -> int | None:
    return int(txt) if txt else None


def siso(txt: str | None) -> datetime | None:
    return datetime.fromisoformat(txt) if txt else None


def scls[C](cls: Callable[..., C], *args: Any, **kwargs: Any) -> C | None:
    if args and args[0] is not None:
        return cls(*args, **kwargs)
