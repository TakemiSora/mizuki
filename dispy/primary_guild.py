from __future__ import annotations
from typing import Any
from .asset import Asset
from .snowflake import Snowflake
from datetime import datetime

class UserPrimaryGuild:
    def __init__(self, data: dict[str, Any]):
        self.id = Snowflake._from_str(data.get("identity_guild_id"))
        self.enabled: bool | None = data.get("identity_enabled")
        self.tag: str | None = data.get("tag")
        self.badge = Asset._from_guild_tag_badge(self.id, data.get("badge"))

    @classmethod
    def _from_dict(cls, data: dict[str, Any] | None) -> UserPrimaryGuild | None:
        if data is not None:
            return cls(data)
        return None
        
    @property
    def created_at(self) -> datetime | None:
        return self.id.created_at if self.id else None