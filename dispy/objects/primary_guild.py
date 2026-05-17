from __future__ import annotations
from .asset import Asset
from .snowflake import Snowflake
from datetime import datetime
from ..payloads.primary_guild import UserPrimaryGuildPayload

__all__ = (
    "UserPrimaryGuild",
)

class UserPrimaryGuild:
    __slots__ = (
        "id",
        "enabled",
        "tag",
        "badge"
    )
    
    def __init__(self, data: UserPrimaryGuildPayload):
        self.id = Snowflake._from_str(data["identity_guild_id"])
        self.enabled = data["identity_enabled"]
        self.tag= data["tag"]
        self.badge = Asset._from_guild_tag_badge(self.id, data["badge"])

    @classmethod
    def _from_dict(cls, data: UserPrimaryGuildPayload | None) -> UserPrimaryGuild | None:
        if data is not None:
            return cls(data)
        return None
        
    @property
    def created_at(self) -> datetime | None:
        return self.id.created_at if self.id else None