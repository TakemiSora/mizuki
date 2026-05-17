from typing import NotRequired, Required, TypedDict
from .collectibles import CollectiblePayload
from .avatar_decoration import AvatarDecorationPayload
from .user import UserPayload
from ._types import CDNHash, ISO8601Timestamp, Snowflake

class PartialMemberPayload(TypedDict, total=False):
    nick: str | None
    avatar: CDNHash | None
    banner: CDNHash | None
    roles: Required[list[Snowflake]]
    joined_at: Required[ISO8601Timestamp | None]
    premium_since: Required[ISO8601Timestamp | None]
    flags: Required[int]
    pending: bool
    permissions: str
    communication_disabled_until: ISO8601Timestamp | None
    avatar_decoration_data: AvatarDecorationPayload | None
    collectibles: CollectiblePayload
    
class MemberPayload(PartialMemberPayload):
    user: NotRequired[UserPayload]
    deaf: bool
    mute: bool