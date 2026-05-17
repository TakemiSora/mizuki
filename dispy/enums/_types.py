from typing import Self
from enum import (
    IntEnum as BaseIntEnum,
    StrEnum as BaseStrEnum
)

class IntEnum(BaseIntEnum):
    @classmethod
    def _from_val(cls, val: int | None) -> Self | None:
        if val is not None:
            return cls(val)
        return None
        
class StrEnum(BaseStrEnum):
    @classmethod
    def _from_val(cls, val: str | None) -> Self | None:
        if val is not None:
            return cls(val)
        return None
