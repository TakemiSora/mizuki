from typing import TypedDict
from mizuki.payloads._types import CDNHash, Snowflake


class UserPrimaryGuildPayload(TypedDict):
    identity_guild_id: Snowflake | None
    identity_enabled: bool | None
    tag: str | None
    badge: CDNHash | None
