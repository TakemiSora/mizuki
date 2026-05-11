from __future__ import annotations
from datetime import datetime, UTC
from .utils import sint

class Snowflake(int):
    _DISCORD_EPOCH = 1420070400000
    __slots__ = ()
    
    @property
    def created_at(self) -> datetime:
        timestamp = ((self.id >> 22) + self._DISCORD_EPOCH) / 1000
        return datetime.fromtimestamp(timestamp, UTC)
        
    @classmethod
    def _from_str(cls, id: str | None) -> Snowflake | None:
        val = sint(id)
        return cls(val) if val else None