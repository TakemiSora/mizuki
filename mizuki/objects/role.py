from datetime import datetime

from mizuki._utils import scls
from mizuki.payloads.role import (
    RoleColorsPayload,
    RoleTagsPayload,
    PartialRolePayload,
    RolePayload
)
from mizuki.objects.asset import Asset
from mizuki.objects.permissions import Permissions
from mizuki.objects.snowflake import Snowflake
from mizuki.flags import RoleFlags

__all__ = (
    "PartialRole",
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

class PartialRole:
    __slots__ = (
        "id",
        "name",
        "colors",
        "icon",
        "unicode_emoji",
        "position"
    )

    def __init__(self, data: PartialRolePayload):
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.colors = RoleColors(data["colors"])
        self.icon = Asset._from_role_icon(self.id, data.get("icon"))
        self.unicode_emoji = data.get("unicode_emoji")
        self.position = data["position"]

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented

    def __hash__(self) -> int:
        return self.id

    @property
    def created_at(self) -> datetime:
        return self.id.created_at

class Role(PartialRole):
    __slots__ = (
        "hoist",
        "permissions",
        "managed",
        "mentionable",
        "tags",
        "flags"
    )

    def __init__(self, data: RolePayload):
        super().__init__(data)
        self.hoist = data["hoist"]
        self.permissions = Permissions(int(data["permissions"]))
        self.managed = data["managed"]
        self.mentionable = data["mentionable"]
        self.tags = scls(RoleTags, data.get("tags"))
        self.flags = RoleFlags(data["flags"])