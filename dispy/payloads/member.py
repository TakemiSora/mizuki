from typing import NotRequired, TypedDict
from .collectibles import CollectiblePayload
from .avatar_decoration import AvatarDecorationPayload
from .user import UserPayload
from ._types import CDNHash, ISO8601Timestamp, Snowflake

class MemberPayload(TypedDict):
    user: NotRequired[UserPayload]
    nick: NotRequired[str | None]
    avatar: NotRequired[CDNHash | None]
    banner: NotRequired[CDNHash | None]
    roles: list[Snowflake]
    joined_at: ISO8601Timestamp | None
    premium_since: ISO8601Timestamp | None
    deaf: bool
    mute: bool
    flags: int
    pending: NotRequired[bool]
    permissions: NotRequired[str]
    communication_disabled_until: NotRequired[ISO8601Timestamp | None]
    avatar_decoration_data: NotRequired[AvatarDecorationPayload | None]
    collectibles: NotRequired[CollectiblePayload]