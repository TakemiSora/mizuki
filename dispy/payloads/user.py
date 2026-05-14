from typing import TypedDict, NotRequired
from .avatar_decoration import AvatarDecorationPayload
from .collectibles import CollectiblePayload
from .primary_guild import UserPrimaryGuildPayload
from ._types import CDNHash, Snowflake

class UserPayload(TypedDict):
    id: Snowflake
    username: str
    discriminator: str
    global_name: str | None
    avatar: CDNHash | None
    bot: NotRequired[bool]
    system: NotRequired[bool]
    mfa_enabled: NotRequired[bool]
    banner: NotRequired[CDNHash | None]
    accent_color: NotRequired[int | None]
    locale: NotRequired[str]
    verified: NotRequired[bool]
    email: NotRequired[str | None]
    flags: NotRequired[int]
    premium_type: NotRequired[int]
    public_flags: NotRequired[int]
    avatar_decoration_data: NotRequired[AvatarDecorationPayload | None]
    collectibles: NotRequired[CollectiblePayload | None]
    primary_guild: NotRequired[UserPrimaryGuildPayload | None]