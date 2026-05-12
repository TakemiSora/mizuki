from typing import TypedDict

class UserPrimaryGuildPayload(TypedDict):
    identity_guild_id: str | None
    identity_enabled: bool | None
    tag: str | None
    badge: str | None