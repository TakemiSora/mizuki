from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, cast, overload

from mizuki._utils import _MISSING, JSONPayload, assign_val_dict, mgetattr, scls, siso
from mizuki.enums.guild import (
    EventRecurrenceRuleFrequency,
    EventRecurrenceRuleMonth,
    EventRecurrenceRuleWeekday,
    GuildExplicitContentLevel,
    GuildFeature,
    GuildMFALevel,
    GuildNotificationLevel,
    GuildNSFWLevel,
    GuildPremiumTier,
    GuildScheduledEventEntityType,
    GuildScheduledEventStatus,
    GuildVerificationLevel,
)
from mizuki.flags import ChannelFlags, SystemChannelFlags
from mizuki.objects.asset import Asset
from mizuki.objects.channel import ThreadChannel, parse_channel_payload
from mizuki.objects.emoji import Emoji
from mizuki.objects.member import Member
from mizuki.objects.presence import Presence
from mizuki.objects.role import Role
from mizuki.objects.snowflake import Snowflake
from mizuki.objects.sticker import Sticker
from mizuki.objects.user import User
from mizuki.payloads.guild import (
    EntityMetadataPayload,
    GuildBanPayload,
    GuildPayload,
    GuildPreviewPayload,
    GuildScheduledEventPayload,
    GuildScheduledEventRecurrenceRulePayload,
    RecurrenceRuleNWeekdayPayload,
    StageInstancePayload,
    UnavailableGuildPayload,
)

if TYPE_CHECKING:
    from mizuki.state import ConnectionState

__all__ = ("ChannelPositionChange", "Guild", "GuildScheduledEvent", "UnavailableGuild")


class UnavailableGuild:
    __slots__ = ("id", "unavailable")

    def __init__(self, data: UnavailableGuildPayload):
        self.id = Snowflake(data["id"])
        self.unavailable = data.get("unavailable", False)


class StageInstance:
    __slots__ = ("channel_id", "guild_id", "guild_scheduled_event_id", "id", "topic")

    def __init__(self, data: StageInstancePayload):
        self.id = Snowflake(data["id"])
        self.guild_id = Snowflake(data["guild_id"])
        self.channel_id = Snowflake(data["channel_id"])
        self.topic = data["topic"]
        self.guild_scheduled_event_id = Snowflake._from_str(
            data["guild_scheduled_event_id"]
        )


class EntityMetadata:
    __slots__ = ("location",)

    def __init__(self, data: EntityMetadataPayload):
        self.location = data.get("location")


class RecurrenceRuleNWeekday:
    __slots__ = ("day", "n")

    def __init__(self, data: RecurrenceRuleNWeekdayPayload):
        self.n = data["n"]
        self.day = EventRecurrenceRuleWeekday(data["day"])


class GuildScheduledEventRecurrenceRule:
    __slots__ = (
        "by_month",
        "by_month_day",
        "by_n_weekday",
        "by_weekday",
        "by_year_day",
        "count",
        "end",
        "frequency",
        "interval",
        "start",
    )

    def __init__(self, data: GuildScheduledEventRecurrenceRulePayload):
        self.start = datetime.fromisoformat(data["start"])
        self.end = siso(data["end"])
        self.frequency = EventRecurrenceRuleFrequency(data["frequency"])
        self.by_weekday = (
            [EventRecurrenceRuleWeekday(e) for e in d]
            if (d := data["by_weekday"])
            else []
        )
        self.by_n_weekday = scls(RecurrenceRuleNWeekday, data["by_n_weekday"])
        self.by_month = scls(EventRecurrenceRuleMonth, data["by_month"])
        self.by_month_day = d if (d := data["by_month_day"]) is not None else []
        self.by_year_day = d if (d := data["by_year_day"]) is not None else []
        self.count = data["count"]


class GuildScheduledEvent:
    __slots__ = (
        "channel_id",
        "creator",
        "creator_id",
        "description",
        "entity_id",
        "entity_metadata",
        "entity_type",
        "guild_id",
        "id",
        "image",
        "name",
        "privacy_level",
        "recurrence_rule",
        "scheduled_end_time",
        "scheduled_start_time",
        "status",
        "user_count",
    )

    def __init__(self, data: GuildScheduledEventPayload, *, state: ConnectionState):
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
        self.creator = scls(User, data.get("creator"), state=state)
        self.user_count = data.get("user_count")
        self.image = Asset._from_guild_scheduled_event_cover(self.id, data.get("image"))
        self.recurrence_rule = scls(
            GuildScheduledEventRecurrenceRule, data["recurrence_rule"]
        )


class GuildPreview:
    __slots__ = (
        "_state",
        "approximate_member_count",
        "approximate_presence_count",
        "description",
        "discovery_splash",
        "emojis",
        "features",
        "icon",
        "id",
        "name",
        "splash",
        "stickers",
    )

    def __init__(self, data: GuildPreviewPayload, *, state: ConnectionState) -> None:
        self._state = state
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.icon = Asset._from_guild_avatar(self.id, data["icon"])
        self.splash = Asset._from_guild_splash(self.id, data["splash"])
        self.discovery_splash = Asset._from_guild_discovery_splash(
            self.id, data["discovery_splash"]
        )
        self.emojis = [Emoji(e, state=self._state) for e in data["emojis"]]
        self.features = [GuildFeature(g) for g in data["features"]]
        self.approximate_member_count = data["approximate_member_count"]
        self.approximate_presence_count = data["approximate_presence_count"]
        self.description = data["description"]
        self.stickers = [Sticker(s, state=self._state) for s in data["stickers"]]

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


class Guild:
    __slots__ = (
        "_state",
        "afk_channel_id",
        "afk_timeout",
        "application_id",
        "approximate_member_count",
        "approximate_presence_count",
        "banner",
        "channels",
        "default_message_notifications",
        "description",
        "discovery_splash",
        "emojis",
        "explicit_level",
        "features",
        "guild_scheduled_events",
        "icon",
        "id",
        "joined_at",
        "large",
        "max_members",
        "max_presences",
        "max_stage_video_channel_users",
        "max_video_channel_users",
        "member_count",
        "members",
        "mfa_level",
        "name",
        "nsfw_level",
        "owner_id",
        "preferred_locale",
        "premium_progress_bar_enabled",
        "premium_subscription_count",
        "premium_tier",
        "presences",
        "public_updates_channel_id",
        "roles",
        "rules_channel_id",
        "safety_alerts_channel_id",
        "soundboard_sounds",
        "splash",
        "stage_instances",
        "stickers",
        "system_channel_flags",
        "system_channel_id",
        "threads",
        "vanity_url_code",
        "verification_level",
        "voice_states",
    )

    def __init__(self, data: GuildPayload, *, state: ConnectionState):
        self._state = state
        self.id = Snowflake(data["id"])
        self.name = data["name"]
        self.icon = Asset._from_guild_avatar(self.id, data.get("icon"))
        self.splash = Asset._from_guild_splash(self.id, data.get("splash"))
        self.discovery_splash = Asset._from_guild_discovery_splash(
            self.id, data.get("discovery_splash")
        )
        self.owner_id = Snowflake(data["owner_id"])
        self.afk_channel_id = Snowflake._from_str(data["afk_channel_id"])
        self.afk_timeout = data["afk_timeout"]
        self.verification_level = GuildVerificationLevel(data["verification_level"])
        self.default_message_notifications = GuildNotificationLevel(
            data["default_message_notifications"]
        )
        self.explicit_level = GuildExplicitContentLevel(data["explicit_content_filter"])
        self.roles = [Role(r) for r in data["roles"]]
        self.emojis = [Emoji(e, state=state) for e in data["emojis"]]
        self.features = {GuildFeature(f) for f in data["features"]}
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
        self.public_updates_channel_id = Snowflake._from_str(
            data["public_updates_channel_id"]
        )
        self.max_video_channel_users = data.get("max_video_channel_users")
        self.max_stage_video_channel_users = data.get("max_stage_video_channel_users")
        self.approximate_member_count = data.get("approximate_member_count")
        self.approximate_presence_count = data.get("approximate_presence_count")
        self.nsfw_level = GuildNSFWLevel(data["nsfw_level"])
        self.stickers = [Sticker(s, state=state) for s in data.get("stickers", [])]
        self.premium_progress_bar_enabled = data["premium_progress_bar_enabled"]
        self.safety_alerts_channel_id = Snowflake._from_str(
            data["safety_alerts_channel_id"]
        )

        self.joined_at = siso(data.get("joined_at"))
        self.large = data.get("large", False)
        self.member_count = data.get("member_count")
        self.members = [
            Member(m, guild_id=self.id, state=state) for m in data.get("members", [])
        ]
        self.channels = [
            parse_channel_payload(c, self.id, state=self._state)
            for c in data.get("channels", [])
        ]
        self.threads = [
            ThreadChannel(c, self.id, state=self._state)
            for c in data.get("threads", [])
        ]
        self.presences = [Presence(p, state=state) for p in data.get("presences", [])]
        self.stage_instances = [
            StageInstance(s) for s in data.get("stage_instances", [])
        ]
        self.guild_scheduled_events = [
            GuildScheduledEvent(g, state=state)
            for g in data.get("guild_scheduled_events", [])
        ]

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
def parse_guild_payload(data: GuildPayload, *, state: ConnectionState) -> Guild: ...


@overload
def parse_guild_payload(
    data: UnavailableGuildPayload, *, state: ConnectionState = _MISSING
) -> UnavailableGuild: ...


def parse_guild_payload(
    data: GuildPayload | UnavailableGuildPayload, *, state: ConnectionState = _MISSING
) -> Guild | UnavailableGuild:
    unavailable = data.get("unavailable", False)
    if unavailable:
        return UnavailableGuild(cast(UnavailableGuildPayload, data))
    else:
        return Guild(cast(GuildPayload, data), state=state)


class GuildBan:
    __slots__ = ("_state", "reason", "user")

    reason: str | None
    user: User

    def __init__(self, data: GuildBanPayload, *, state: ConnectionState) -> None:
        self._state = state
        self.reason = data["reason"]
        self.user = User(data["user"], state=self._state)


@dataclass(slots=True)
class ChannelPositionChange:
    id: int
    position: int | None = _MISSING
    lock_permissions: bool | None = _MISSING
    parent_id: int | None = _MISSING
    flags: ChannelFlags | None = _MISSING

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {"id": self.id},
            _MISSING,
            position=self.position,
            lock_permissions=self.lock_permissions,
            parent_id=self.parent_id,
            flags=mgetattr(self.flags, "value"),
        )


@dataclass(slots=True)
class BulkBanResult:
    banned_users: list[int]
    failed_users: list[int]

    @classmethod
    def _from_dict(cls, data: dict[str, list[str]]) -> BulkBanResult:
        return cls(
            banned_users=[int(v) for v in data["banned_users"]],
            failed_users=[int(v) for v in data["failed_users"]],
        )
