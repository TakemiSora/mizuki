from typing import TypedDict, NotRequired
from .user import UserPayload
from ._types import Snowflake

class PartialEmojiPayload(TypedDict):
    id: Snowflake | None
    name: str | None
    animated: NotRequired[bool]

class EmojiPayload(TypedDict):
    id: Snowflake
    name: str
    roles: list[Snowflake]
    user: NotRequired[UserPayload]
    require_colons: NotRequired[bool]
    managed: NotRequired[bool]
    animated: NotRequired[bool]
    available: NotRequired[bool]