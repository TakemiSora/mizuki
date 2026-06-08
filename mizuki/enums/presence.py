from enum import IntEnum, StrEnum

__all__ = (
    "ActivityType",
    "StatusDisplayType",
    "PresenceStatusType",
)

class ActivityType(IntEnum):
    Playing = 0
    Streaming = 1
    Listening = 2
    Watching = 3
    Custom = 4
    Competing = 5

class StatusDisplayType(IntEnum):
    Name = 0
    State = 1
    Details = 2

class PresenceStatusType(StrEnum):
    idle = "idle"
    dnd = "dnd"
    online = "online"
    offline = "offline"