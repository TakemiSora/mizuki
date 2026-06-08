from typing import NotRequired, TypedDict, Literal
from .emoji import EmojiPayload
from .role import RolePayload
from .sticker import StickerPayload
from ._types import UNIMPLEMENTED, ISO8601Timestamp, Snowflake, CDNHash
from .member import MemberPayload
from .channel import GuildChannelPayload, ThreadPayload
from .user import UserPayload
from .presence import PresencePayload

class UnavailableGuildPayload(TypedDict):
    id: Snowflake
    unavailable: NotRequired[Literal[True]]

class StageInstancePayload(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Snowflake
    topic: str
    guild_scheduled_event_id: Snowflake | None
    
class EntityMetadataPayload(TypedDict, total=False):
    location: str

RecurrenceRuleWeekday = Literal[0, 1, 2, 3, 4, 5, 6]
RecurrenceRuleMonth = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

class RecurrenceRuleNWeekdayPayload(TypedDict):
    n: int
    day: RecurrenceRuleWeekday

class GuildScheduledEventRecurrenceRulePayload(TypedDict):
    start: ISO8601Timestamp
    end: ISO8601Timestamp | None
    frequency: Literal[0, 1, 2, 3, 4]
    interval: int
    by_weekday: list[RecurrenceRuleWeekday] | None
    by_n_weekday: RecurrenceRuleNWeekdayPayload | None
    by_month: RecurrenceRuleMonth | None
    by_month_day: list[int] | None
    by_year_day: list[int] | None
    count: int | None
    
class GuildScheduledEventPayload(TypedDict):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Snowflake | None
    creator_id: NotRequired[Snowflake | None]
    name: str
    description: NotRequired[str | None]
    scheduled_start_time: ISO8601Timestamp
    scheduled_end_time: ISO8601Timestamp | None
    privacy_level: Literal[2]
    status: Literal[1, 2, 3, 4]
    entity_type: Literal[1, 2, 3]
    entity_id: Snowflake | None
    entity_metadata: EntityMetadataPayload | None
    creator: NotRequired[UserPayload]
    user_count: NotRequired[int]
    image: NotRequired[CDNHash | None]
    recurrence_rule: GuildScheduledEventRecurrenceRulePayload | None

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
    joined_at: NotRequired[ISO8601Timestamp]
    large: NotRequired[bool]
    member_count: NotRequired[int]
    voice_states: NotRequired[list[UNIMPLEMENTED]]
    members: NotRequired[list[MemberPayload]]
    channels: NotRequired[list[GuildChannelPayload]]
    threads: NotRequired[list[ThreadPayload]]
    presences: NotRequired[list[PresencePayload]]
    stage_instances: NotRequired[list[StageInstancePayload]]
    guild_scheduled_events: NotRequired[list[GuildScheduledEventPayload]]
    soundboard_sounds: NotRequired[list[UNIMPLEMENTED]]
    unavailable: NotRequired[Literal[False]]