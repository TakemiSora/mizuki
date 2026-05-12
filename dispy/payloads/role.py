from typing import NotRequired, TypedDict

class RoleColorsPayload(TypedDict):
    primary_color: int
    secondary_color: int | None
    tertiary_color: int | None

class RoleTagsPayload(TypedDict):
    bot_id: NotRequired[str]
    integration_id: NotRequired[str]
    premium_subscriber: NotRequired[None]
    subscription_listing_id: NotRequired[str]
    available_for_purchase: NotRequired[None]
    guild_connections: NotRequired[None]

class RolePayload(TypedDict):
    id: str
    name: str
    colors: RoleColorsPayload
    hoist: bool
    icon: NotRequired[str | None]
    unicode_emoji: NotRequired[str | None]
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: NotRequired[RoleTagsPayload]
    flags: int