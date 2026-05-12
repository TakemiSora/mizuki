from typing import NotRequired, TypedDict
from .user import UserPayload

class StickerPayload(TypedDict):
    id: str
    pack_id: NotRequired[str]
    name: str
    description: str | None
    tags: str
    type: int
    format_type: int
    available: NotRequired[bool]
    guild_id: NotRequired[str]
    user: NotRequired[UserPayload]
    sort_value: NotRequired[int]