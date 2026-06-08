from __future__ import annotations
from typing import Required, TypedDict, TYPE_CHECKING

from ._types import CDNHash, Snowflake
from .avatar_decoration import AvatarDecorationPayload
from .collectibles import CollectiblePayload
from .primary_guild import UserPrimaryGuildPayload
if TYPE_CHECKING:
    from .member import PartialMemberPayload

class PartialUserPayload(TypedDict):
    id: Snowflake

class UserPayload(PartialUserPayload, total=False):
    username: Required[str]
    discriminator: Required[str]
    global_name: Required[str | None]
    avatar: Required[CDNHash | None]
    bot: bool
    system: bool
    mfa_enabled: bool
    banner: CDNHash | None
    accent_color: int | None
    locale: str
    verified: bool
    email: str | None
    flags: int
    premium_type: int
    public_flags: int
    avatar_decoration_data: AvatarDecorationPayload | None
    collectibles: CollectiblePayload | None
    primary_guild: UserPrimaryGuildPayload | None
    member: PartialMemberPayload