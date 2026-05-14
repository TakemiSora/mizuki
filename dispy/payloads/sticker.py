from typing import NotRequired, TypedDict
from .user import UserPayload
from ._types import Snowflake

class StickerPayload(TypedDict):
    id: Snowflake
    pack_id: NotRequired[Snowflake]
    name: str
    description: str | None
    tags: str
    type: int
    format_type: int
    available: NotRequired[bool]
    guild_id: NotRequired[Snowflake]
    user: NotRequired[UserPayload]
    sort_value: NotRequired[int]