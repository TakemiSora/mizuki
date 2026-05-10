from __future__ import annotations
from typing import Any
from .http import get_state
from .asset import Asset

class UserPrimaryGuild:
    def __init__(self, data: dict[str, Any]):
        self.id = int(data.get("identity_guild_id")) if "identity_guild_id" in data else None
        self.enabled: bool | None = data.get("identity_enabled")
        self.tag: str | None = data.get("tag")
        self.badge = Asset._from_guild_tag_badge(self.id, data.get("badge"))

    @classmethod
    def _from_dict(cls, data: dict[str, Any] | None) -> UserPrimaryGuild | None:
        if data is not None:
            return cls(data)
        return None
