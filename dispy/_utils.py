from datetime import datetime
from typing import Any, Protocol
from collections.abc import Callable

class Missing:
    __slots__ = ()

    def __bool__(self) -> bool:
        return False

_MISSING: Any = Missing()

class SupportsToDict(Protocol):
    def _to_dict(self) -> Any: ...

def assign_val[T](obj: T, keys: dict[str, Any], check_against: Any = _MISSING) -> T:
    for key, val in keys.items():
        if val is not check_against: setattr(obj, key, val)
    return obj

def mtd[T: SupportsToDict](obj: T | None) -> T | None:
    return obj._to_dict() if obj is not None else None

def assign_val_dict[T](d: T, keys: dict[str, Any], check_against: Any = None) -> T:
    for key, val in keys.items():
        if val is not check_against: d[key] = val # type: ignore
    return d

def sint(txt: str | None) -> int | None:
    return int(txt) if txt else None

def siso(txt: str | None) -> datetime | None:
    return datetime.fromisoformat(txt) if txt else None

def scls[C](cls: Callable[..., C], data: Any, **kwargs: Any) -> C | None:
    return cls(data, **kwargs) if data else None