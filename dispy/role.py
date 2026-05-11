from __future__ import annotations
from typing import Any
from .asset import Asset
from .flags import RoleFlags
from .permissions import Permissions
from .snowflake import Snowflake
from datetime import datetime

class RoleColors:
    def __init__(self, data: dict[str, int | None]):
        self.primary: int = data["primary_color"]
        self.secondary = data.get("secondary_color")
        self.tertiary = data.get("tertiary_color")
        
class RoleTags:
    def __init__(self, data: dict[str, Any]):
        self.bot_id = Snowflake._from_str(data.get("bot_id"))
        self.integration_id = Snowflake._from_str(data.get("integration_id"))
        self.premium_subscriber: bool = "premium_subscriber" in data
        self.subscription_listing_id = Snowflake._from_str(data.get("subscription_listing_id"))
        self.available_for_purchase: bool = "available_for_purchase" in data
        self.guild_connections: bool = "guild_connections" in data
        
    @classmethod
    def _from_dict(cls, data: dict[str, Any] | None) -> RoleTags | None:
        return cls(data) if data is not None else None
            
class Role:
    def __init__(self, data: dict[str, Any]):            
        self.id = Snowflake(data["id"])
        self.name: str = data["name"]
        self.colors = RoleColors(data["colors"])
        self.hoist: bool = data["hoist"]
        self.icon = Asset._from_role_icon(self.id, data.get("icon"))
        self.emoji: str | None = data.get("unicode_emoji")
        self.position: int = data["position"]
        self.permissions = Permissions(int(data["permissions"]))
        self.managed: bool = data["managed"]
        self.mentionable: bool = data["mentionable"]
        self.flags = RoleFlags(data["flags"])
        self.tags = RoleTags._from_dict(data.get("tags"))
        
    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented
    
    def __hash__(self) -> int:
        return self.id
            
    @property
    def created_at(self) -> datetime:
        return self.id.created_at