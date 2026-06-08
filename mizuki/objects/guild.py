from typing import cast, overload
from .asset import Asset
from ..enums.guild import (
    EventRecurrenceRuleMonth,
    EventRecurrenceRuleWeekday,
    GuildScheduledEventEntityType,
    EventRecurrenceRuleFrequency,
    GuildVerificationLevel,
    GuildNotificationLevel,
    GuildExplicitContentLevel,
    GuildFeature, GuildMFALevel,
    GuildPremiumTier, GuildNSFWLevel,
    GuildScheduledEventStatus
)
from ..payloads.guild import (
    EntityMetadataPayload,
    GuildPayload,
    GuildScheduledEventPayload,
    GuildScheduledEventRecurrenceRulePayload,
    RecurrenceRuleNWeekdayPayload,
    StageInstancePayload,
    UnavailableGuildPayload
)
from ..flags import SystemChannelFlags
from .sticker import Sticker
from .role import Role
from .presence import Presence
from .user import User
from .emoji import Emoji
from .snowflake import Snowflake
from .member import Member
from .channel import ThreadChannel, parse_channel_payload
from datetime import datetime
from .._utils import siso, scls

__all__ = (
    "UnavailableGuild",
    "GuildScheduledEvent",
    "Guild",
)

class UnavailableGuild:
    __slots__ = (
        "id",
        "unavailable"
    )
    
    def __init__(self, data: UnavailableGuildPayload):
        self.id = Snowflake(data["id"])
        self.unavailable = data.get("unavailable", False)

class StageInstance:
    __slots__ = (
        "id",
        "guild_id",
        "channel_id",
        "topic",
        "guild_scheduled_event_id"
    )

    def __init__(self, data: StageInstancePayload):
        self.id = Snowflake(data["id"])
        self.guild_id = Snowflake(data["guild_id"])
        self.channel_id = Snowflake(data["channel_id"])
        self.topic = data["topic"]
        self.guild_scheduled_event_id = Snowflake._from_str(data["guild_scheduled_event_id"])

class EntityMetadata:
    __slots__ = (
        "location",
    )
    
    def __init__(self, data: EntityMetadataPayload):
        self.location = data.get("location")
        
class RecurrenceRuleNWeekday:
    __slots__ = (
        "n",
        "day"
    )
    
    def __init__(self, data: RecurrenceRuleNWeekdayPayload):
        self.n = data["n"]
        self.day = EventRecurrenceRuleWeekday(data["day"])
        
class GuildScheduledEventRecurrenceRule:
    __slots__ = (
        "start",
        "end",
        "frequency",
        "interval",
        "by_weekday",
        "by_n_weekday",
        "by_month",
        "by_month_day",
        "by_year_day",
        "count"
    )
    
    def __init__(self, data: GuildScheduledEventRecurrenceRulePayload):
        self.start = datetime.fromisoformat(data["start"])
        self.end = siso(data["end"])
        self.frequency = EventRecurrenceRuleFrequency(data["frequency"])
        self.by_weekday = [EventRecurrenceRuleWeekday(e) for e in d] if (d := data["by_weekday"]) else []
        self.by_n_weekday= scls(RecurrenceRuleNWeekday, data["by_n_weekday"])
        self.by_month = scls(EventRecurrenceRuleMonth, data["by_month"])
        self.by_month_day = d if (d := data["by_month_day"]) is not None else []
        self.by_year_day = d if (d := data["by_year_day"]) is not None else []
        self.count = data["count"]
        
class GuildScheduledEvent:
    __slots__ = (
        "id",
        "guild_id",
        "channel_id",
        "creator_id",
        "name",
        "description",
        "scheduled_start_time",
        "scheduled_end_time",
        "privacy_level",
        "status",
        "entity_type",
        "entity_id",
        "entity_metadata",
        "creator",
        "user_count",
        "image",
        "recurrence_rule"
    )
    
    def __init__(self, data: GuildScheduledEventPayload):
        self.id = Snowflake(data["id"])
        self.guild_id = Snowflake(data["guild_id"])
        self.channel_id = Snowflake._from_str(data["channel_id"])
        self.creator_id = Snowflake._from_str(data.get("creator_id"))
        self.name = data["name"]
        self.description = data.get("description")
        self.scheduled_start_time = datetime.fromisoformat(data["scheduled_start_time"])
        self.scheduled_end_time = siso(data["scheduled_end_time"])
        self.privacy_level = data["privacy_level"]
        self.status = GuildScheduledEventStatus(data["status"])
        self.entity_type = GuildScheduledEventEntityType(data["entity_type"])
        self.entity_id = Snowflake._from_str(data["entity_id"])
        self.entity_metadata = scls(EntityMetadata, data["entity_metadata"])
        self.creator = scls(User, data.get("creator"))
        self.user_count = data.get("user_count")
        self.image = Asset._from_guild_scheduled_event_cover(self.id, data.get("image"))
        self.recurrence_rule = scls(GuildScheduledEventRecurrenceRule, data["recurrence_rule"])
        
class Guild:
    __slots__ = (
        "id",
        "name",
        "icon",
        "splash",
        "discovery_splash",
        "owner_id",
        "afk_channel_id",
        "afk_timeout",
        "verification_level",
        "default_message_notifications",
        "explicit_level",
        "roles",
        "emojis",
        "features",
        "mfa_level",
        "application_id",
        "system_channel_id",
        "system_channel_flags",
        "rules_channel_id",
        "max_presences",
        "max_members",
        "vanity_url_code",
        "description",
        "banner",
        "premium_tier",
        "premium_subscription_count",
        "preferred_locale",
        "public_updates_channel_id",
        "max_video_channel_users",
        "max_stage_video_channel_users",
        "approximate_member_count",
        "approximate_presence_count",
        "nsfw_level",
        "stickers",
        "premium_progress_bar_enabled",
        "safety_alerts_channel_id",
        "joined_at",
        "large",
        "member_count",
        "voice_states",
        "members",
        "channels",
        "threads",
        "presences",
        "stage_instances",
        "guild_scheduled_events",
        "soundboard_sounds",
    )
    
    def __init__(self, data: GuildPayload):
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.icon = Asset._from_guild_avatar(self.id, data.get("icon"))
        self.splash = Asset._from_guild_splash(self.id, data.get("splash"))
        self.discovery_splash = Asset._from_guild_discovery_splash(self.id, data.get("discovery_splash"))
        self.owner_id = Snowflake(data["owner_id"])
        self.afk_channel_id = Snowflake._from_str(data["afk_channel_id"])
        self.afk_timeout = data["afk_timeout"]
        self.verification_level = GuildVerificationLevel(data["verification_level"])
        self.default_message_notifications = GuildNotificationLevel(data["default_message_notifications"])
        self.explicit_level = GuildExplicitContentLevel(data["explicit_content_filter"])
        self.roles = [Role(r) for r in data["roles"]]
        self.emojis = [Emoji(e) for e in data["emojis"]]
        self.features = set(GuildFeature(f) for f in data["features"])
        self.mfa_level = GuildMFALevel(data["mfa_level"])
        self.application_id = Snowflake._from_str(data["application_id"])
        self.system_channel_id = Snowflake._from_str(data["system_channel_id"])
        self.system_channel_flags = SystemChannelFlags(data["system_channel_flags"])
        self.rules_channel_id = data["rules_channel_id"]
        self.max_presences = data.get("max_presences")
        self.max_members = data.get("max_members")
        self.vanity_url_code = data["vanity_url_code"]
        self.description = data.get("description")
        self.banner = Asset._from_guild_banner(self.id, data["banner"])
        self.premium_tier = GuildPremiumTier(data["premium_tier"])
        self.premium_subscription_count: int = data.get("premium_subscription_count", 0)
        self.preferred_locale = data["preferred_locale"]
        self.public_updates_channel_id = Snowflake._from_str(data["public_updates_channel_id"])
        self.max_video_channel_users = data.get("max_video_channel_users")
        self.max_stage_video_channel_users = data.get("max_stage_video_channel_users")
        self.approximate_member_count = data.get("approximate_member_count")
        self.approximate_presence_count = data.get("approximate_presence_count")
        self.nsfw_level = GuildNSFWLevel(data["nsfw_level"])
        self.stickers = [Sticker(s) for s in data.get("stickers", [])]
        self.premium_progress_bar_enabled = data["premium_progress_bar_enabled"]        
        self.safety_alerts_channel_id = Snowflake._from_str(data["safety_alerts_channel_id"])

        self.joined_at = siso(data.get("joined_at"))
        self.large = data.get("large", False)
        self.member_count = data.get("member_count")
        self.members = [Member(m, guild_id=self.id) for m in data.get("members", [])]
        self.channels = [parse_channel_payload(c, self.id) for c in data.get("channels", [])]
        self.threads = [ThreadChannel(c, self.id) for c in data.get("threads", [])]
        self.presences = [Presence(p) for p in data.get("presences", [])]
        self.stage_instances = [StageInstance(s) for s in data.get("stage_instances", [])]
        self.guild_scheduled_events = [GuildScheduledEvent(g) for g in data.get("guild_scheduled_events", [])]
        
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented
    
    def __hash__(self) -> int:
        return self.id
            
    @property
    def created_at(self) -> datetime:
        return self.id.created_at

@overload
def parse_guild_payload(data: GuildPayload) -> Guild: ...
    
@overload
def parse_guild_payload(data: UnavailableGuildPayload) -> UnavailableGuild: ...
        
def parse_guild_payload(data: GuildPayload | UnavailableGuildPayload) -> Guild | UnavailableGuild:
    unavailable = data.get("unavailable", False)
    if unavailable:
        return UnavailableGuild(cast(UnavailableGuildPayload, data))
    else:
        return Guild(cast(GuildPayload, data))