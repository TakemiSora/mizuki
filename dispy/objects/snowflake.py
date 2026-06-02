from typing import Self
from datetime import datetime, UTC
from .._utils import sint

class Snowflake(int):
    """
    Represents a Discord Snowflake.
    """
    
    _DISCORD_EPOCH = 1420070400000
    __slots__ = ()
    
    @property
    def created_at(self) -> datetime:
        """
        The time at which this Snowflake was created.
        
        Returns
        -------
        :class:`datetime <datetime.datetime>`
            The datetime object representing the time at which this Snowflake was created.
        """
        timestamp = ((self >> 22) + self._DISCORD_EPOCH) / 1000
        return datetime.fromtimestamp(timestamp, UTC)
        
    @classmethod
    def _from_str(cls, id: str | None) -> Self | None:
        val = sint(id)
        return cls(val) if val else None