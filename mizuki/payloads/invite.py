from typing import TypedDict, Literal, Required

from ._types import UNIMPLEMENTED, ISO8601Timestamp
from .channel import PartialGuildChannelPayload
from .user import UserPayload
from .role import PartialRolePayload
from .guild import GuildPayload, GuildScheduledEventPayload


class InvitePayload(TypedDict, total=False):
    type: Required[Literal[0, 1, 2]]
    code: Required[str]
    guild: GuildPayload
    channel: Required[PartialGuildChannelPayload | None]
    inviter: UserPayload
    target_type: Literal[1, 2]
    target_user: UserPayload
    target_application: UNIMPLEMENTED
    approximate_presence_count: int
    approximate_member_count: int
    expires_at: Required[ISO8601Timestamp | None]
    guild_scheduled_event: GuildScheduledEventPayload
    flags: Literal[0, 1]
    roles: list[PartialRolePayload]


class InviteMetadataPayload(InvitePayload):
    uses: int
    max_uses: int
    max_age: int
    temporary: bool
    created_at: ISO8601Timestamp
