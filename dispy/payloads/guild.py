from typing import NotRequired, TypedDict
from .emoji import EmojiPayload
from .role import RolePayload
from .sticker import StickerPayload
from ._types import Snowflake, CDNHash

class GuildPayload(TypedDict):
    id: Snowflake
    name: str
    icon: CDNHash | None
    icon_hash: NotRequired[CDNHash | None]
    splash: CDNHash | None
    discovery_splash: CDNHash | None
    owner_id: Snowflake
    afk_channel_id: Snowflake | None
    afk_timeout: int
    verification_level: int
    default_message_notifications: int
    explicit_content_filter: int
    roles: list[RolePayload]
    emojis: list[EmojiPayload]
    features: list[str]
    mfa_level: int
    application_id: Snowflake | None
    system_channel_id: Snowflake | None
    system_channel_flags: int
    rules_channel_id: Snowflake | None
    max_presences: NotRequired[int | None]
    max_members: NotRequired[int]
    vanity_url_code: str | None
    description: str | None
    banner: CDNHash | None
    premium_tier: int
    premium_subscription_count: NotRequired[int]
    preferred_locale: str
    public_updates_channel_id: Snowflake | None
    max_video_channel_users: NotRequired[int]
    max_stage_video_channel_users: NotRequired[int]
    approximate_member_count: NotRequired[int]
    approximate_presence_count: NotRequired[int]
    nsfw_level: int
    stickers: NotRequired[list[StickerPayload]]
    premium_progress_bar_enabled: bool
    safety_alerts_channel_id: Snowflake | None