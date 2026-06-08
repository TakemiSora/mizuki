from .asset import Asset
from ..flags import RoleFlags
from .permissions import Permissions
from .snowflake import Snowflake
from datetime import datetime
from ..payloads.role import RoleColorsPayload, RoleTagsPayload, RolePayload
from .._utils import scls

__all__ = (
    "Role",
)

class RoleColors:
    __slots__ = (
        "primary",
        "secondary",
        "tertiary"
    )
    
    def __init__(self, data: RoleColorsPayload):
        self.primary = data["primary_color"]
        self.secondary = data["secondary_color"]
        self.tertiary = data["tertiary_color"]
        
class RoleTags:
    __slots__ = (
        "bot_id",
        "integration_id",
        "premium_subscriber",
        "subscription_listing_id",
        "available_for_purchase",
        "guild_connections"
    )
    
    def __init__(self, data: RoleTagsPayload):
        self.bot_id = Snowflake._from_str(data.get("bot_id"))
        self.integration_id = Snowflake._from_str(data.get("integration_id"))
        self.premium_subscriber = "premium_subscriber" in data
        self.subscription_listing_id = Snowflake._from_str(data.get("subscription_listing_id"))
        self.available_for_purchase = "available_for_purchase" in data
        self.guild_connections = "guild_connections" in data
    
class Role:
    def __init__(self, data: RolePayload):            
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.colors = RoleColors(data["colors"])
        self.hoist = data["hoist"]
        self.icon = Asset._from_role_icon(self.id, data.get("icon"))
        self.emoji = data.get("unicode_emoji")
        self.position = data["position"]
        self.permissions = Permissions(int(data["permissions"]))
        self.managed= data["managed"]
        self.mentionable = data["mentionable"]
        self.tags = scls(RoleTags, data.get("tags"))
        self.flags = RoleFlags(data["flags"])
        
    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented
    
    def __hash__(self) -> int:
        return self.id
            
    @property
    def created_at(self) -> datetime:
        return self.id.created_at