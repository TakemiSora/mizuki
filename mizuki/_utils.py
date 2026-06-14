from datetime import datetime
from typing import Any, Protocol
from collections.abc import Callable, Coroutine

class Missing:
    __slots__ = ()

    def __bool__(self) -> bool:
        return False

_MISSING: Any = Missing()

type CoroFunc = Callable[..., Coroutine[Any, Any, Any]]
type CoroDecorator = Callable[[CoroFunc], CoroFunc]

class SupportsToDict(Protocol):
    def _to_dict(self) -> Any: ...

def assign_val[T](obj: T, check_against: Any = _MISSING, /, **kwargs: Any) -> T:
    for key, val in kwargs.items():
        if val is not check_against: setattr(obj, key, val)
    return obj

def mtd[T: SupportsToDict](obj: T | None) -> T | None:
    if (
        obj is not None
        and obj is not _MISSING
    ): return obj._to_dict()

def assign_val_dict[T](d: T, check_against: Any = None, /, **kwargs: Any) -> T:
    for key, val in kwargs.items():
        if val is not check_against: d[key] = val # type: ignore
    return d

def sint(txt: str | None) -> int | None:
    return int(txt) if txt else None

def siso(txt: str | None) -> datetime | None:
    return datetime.fromisoformat(txt) if txt else None

def scls[C](cls: Callable[..., C], data: Any, **kwargs: Any) -> C | None:
    return cls(data, **kwargs) if data else None