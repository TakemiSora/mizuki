from typing import NotRequired, TypedDict, Literal
from .user import UserPayload
from ._types import Snowflake


class PartialStickerPayload(TypedDict):
    id: Snowflake
    name: str
    format_type: Literal[1, 2, 3, 4]


class StickerPayload(PartialStickerPayload):
    pack_id: NotRequired[Snowflake]
    description: str | None
    tags: str
    type: int
    available: NotRequired[bool]
    guild_id: NotRequired[Snowflake]
    user: NotRequired[UserPayload]
    sort_value: NotRequired[int]
