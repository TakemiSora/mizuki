from datetime import datetime
from typing import Any
from collections.abc import Callable

class Missing:
    __slots__ = ()

    def __bool__(self) -> bool:
        return False

_MISSING: Any = Missing()

def sint(txt: str | None) -> int | None:
    return int(txt) if txt else None

def siso(txt: str | None) -> datetime | None:
    return datetime.fromisoformat(txt) if txt else None

def scls[C](cls: Callable[..., C], data: Any, **kwargs: Any) -> C | None:
    return cls(data, **kwargs) if data else None