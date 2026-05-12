from typing import TypedDict, NotRequired
from .user import UserPayload

class PartialEmojiPayload(TypedDict):
    id: str | None
    name: str | None
    animated: NotRequired[bool]

class EmojiPayload(TypedDict):
    id: str
    name: str
    roles: list[int]
    user: NotRequired[UserPayload]
    require_colons: NotRequired[bool]
    managed: NotRequired[bool]
    animated: NotRequired[bool]
    available: NotRequired[bool]