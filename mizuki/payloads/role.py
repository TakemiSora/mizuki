from typing import NotRequired, TypedDict
from ._types import CDNHash, Permissions, Snowflake

class RoleColorsPayload(TypedDict):
    primary_color: int
    secondary_color: int | None
    tertiary_color: int | None

class RoleTagsPayload(TypedDict):
    bot_id: NotRequired[Snowflake]
    integration_id: NotRequired[Snowflake]
    premium_subscriber: NotRequired[None]
    subscription_listing_id: NotRequired[Snowflake]
    available_for_purchase: NotRequired[None]
    guild_connections: NotRequired[None]

class RolePayload(TypedDict):
    id: Snowflake
    name: str
    colors: RoleColorsPayload
    hoist: bool
    icon: NotRequired[CDNHash | None]
    unicode_emoji: NotRequired[str | None]
    position: int
    permissions: Permissions
    managed: bool
    mentionable: bool
    tags: NotRequired[RoleTagsPayload]
    flags: int