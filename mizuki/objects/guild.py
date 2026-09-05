from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Literal, cast, overload

from mizuki._utils import _MISSING, JSONPayload, assign_val_dict, mgetattr, scls, siso
from mizuki.enums.channel import (
    ChannelType,
    ForumLayoutType,
    SortOrderType,
    VideoQualityMode,
)
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
from mizuki.file import File
from mizuki.flags import ChannelFlags, SystemChannelFlags
from mizuki.objects.asset import Asset
from mizuki.objects.channel import (
    GuildChannel,
    PartialForumTag,
    ThreadChannel,
    ThreadMember,
    parse_channel_payload,
)
from mizuki.objects.emoji import DefaultReaction, Emoji
from mizuki.objects.member import Member
from mizuki.objects.permissions import ChannelPermissionOverwrite, Permissions
from mizuki.objects.presence import Presence
from mizuki.objects.role import Role, RoleColors, RolePositionChange
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
    """Represents a Discord Guild."""

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
        "splash",
        "stage_instances",
        "stickers",
        "system_channel_flags",
        "system_channel_id",
        "threads",
        "vanity_url_code",
        "verification_level",
    )

    id: Snowflake
    "The ID of the guild."

    name: str
    "The name of the guild."

    icon: Asset | None
    "The icon of the guild."

    splash: Asset | None
    "The splash art of the guild."

    discovery_splash: Asset | None
    "The discovery splash art of the guild."

    owner_id: Snowflake
    "The ID of the owner of the guild."

    afk_channel_id: Snowflake | None
    "The ID of the AFK channel of the guild."

    afk_timeout: timedelta
    "The amount of time after which an user can be counted as AFK."

    verification_level: GuildVerificationLevel
    "The verification level required in the guild."

    default_message_notifications: GuildNotificationLevel
    "The default notification settings set for newly joined users."

    explicit_level: GuildExplicitContentLevel
    "Determines which members have the media they sent scanned for explicit content."

    roles: list[Role]
    "The roles in the guild."

    emojis: list[Emoji]
    "The emojis of the guild."

    features: list[GuildFeature]
    "The features currently enabled in the guild."

    mfa_level: GuildMFALevel
    "Whether moderators need to have MFA enabled to be able to moderate."

    application_id: Snowflake | None
    "The ID of the application that created this guild, if it was created by one."

    system_channel_id: Snowflake | None
    "The iD of the channel where messages such as welcome messages, boost messages etc are posted."

    system_channel_flags: SystemChannelFlags
    "The flags of the system channel."

    rules_channel_id: Snowflake | None
    "The ID of the rules channel."

    max_presences: int | None
    "The maximum number of presences for the guild. (Always :obj:`None` except for the largest guilds.)"

    max_members: int | None
    "The max number of members the guild can have."

    vanity_url_code: str | None
    "The vanity URL for the guild."

    description: str | None
    "The description of the guild."

    banner: Asset | None
    "The banner of the guild."

    premium_tier: GuildPremiumTier
    "The server boost level of the guild."

    premium_subscription_count: int | None
    "The number of boosts the server has."

    preferred_locale: str
    "The preferred locale for a community guild, defaults to 'en-US'."

    public_updates_channel_id: Snowflake | None
    "The ID of the channel where admins and moderators recieve notices regarding community guilds."

    max_video_channel_users: int | None
    "The maximum amount of users in a video channel."

    max_stage_video_channel_users: int | None
    "The maximum amount of users in a stage channel."

    approximate_member_count: int | None
    "The member count of the guild, may be :obj:`None` if the guild was fetched with `with_counts` set to :obj:`False`."

    approximate_presence_count: int | None
    "The approximate number of non-offline members of the guild, may be :obj:`None` if the guild was fetched with `with_counts` set to :obj:`False`."

    nsfw_level: GuildNSFWLevel
    "The age restriction level of the guild."

    stickers: list[Sticker]
    "The stickers of the guild."

    premium_progress_bar_enabled: bool
    "Whether the boost progress bar at the top of the channel list is shown or not."

    safety_alert_channel_id: int
    "The ID of the channel where the admins and moderators of commmunity guilds recieve safety alerts from Discord."

    joined_at: datetime | None
    "When the guild was joined at."

    large: bool
    "Whether this guild is considered a large guild."

    member_count: int | None
    "The number of members, may be :obj:`None` in which case use :attr:`~mizuki.Guild.approximate_member_count`."

    members: list[Member]
    "The users in the guild."

    channels: list[GuildChannel]
    "The channels of the guild."

    threads: list[ThreadChannel]
    "The threads that the current guild member can view."

    presences: list[Presence]
    "The presences of the members of the guild, only include non-offline members if the guild is large."

    stage_instances: list[StageInstance]
    "The stage instances in the guild."

    guild_scheduled_events: list[GuildScheduledEvent]
    "The scheduled events in the guild."

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
        self.afk_timeout = timedelta(data["afk_timeout"])
        self.verification_level = GuildVerificationLevel(data["verification_level"])
        self.default_message_notifications = GuildNotificationLevel(
            data["default_message_notifications"]
        )
        self.explicit_level = GuildExplicitContentLevel(data["explicit_content_filter"])
        self.roles = [Role(r) for r in data["roles"]]
        self.emojis = [Emoji(e, state=state) for e in data["emojis"]]
        self.features = [GuildFeature(f) for f in data["features"]]
        self.mfa_level = GuildMFALevel(data["mfa_level"])
        self.application_id = Snowflake._from_str(data["application_id"])
        self.system_channel_id = Snowflake._from_str(data["system_channel_id"])
        self.system_channel_flags = SystemChannelFlags(data["system_channel_flags"])
        self.rules_channel_id = Snowflake._from_str(data["rules_channel_id"])
        self.max_presences = data.get("max_presences")
        self.max_members = data.get("max_members")
        self.vanity_url_code = data["vanity_url_code"]
        self.description = data.get("description")
        self.banner = Asset._from_guild_banner(self.id, data["banner"])
        self.premium_tier = GuildPremiumTier(data["premium_tier"])
        self.premium_subscription_count = data.get("premium_subscription_count", 0)
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

    async def edit_guild(
        self,
        *,
        name: str = _MISSING,
        verification_level: GuildVerificationLevel | None = _MISSING,
        default_message_notifications: GuildNotificationLevel | None = _MISSING,
        explicit_content_filter: GuildExplicitContentLevel | None = _MISSING,
        afk_channel_id: int | None = _MISSING,
        afk_timeout: timedelta | int | None = _MISSING,
        icon: File | str | None = _MISSING,
        splash: File | str | None = _MISSING,
        discovery_splash: File | str | None = _MISSING,
        banner: File | str | None = _MISSING,
        system_channel_id: int | None = _MISSING,
        system_channel_flags: SystemChannelFlags | None = _MISSING,
        rules_channel_id: int | None = _MISSING,
        public_updates_channel_id: int | None = _MISSING,
        preferred_locale: str | None = _MISSING,
        features: list[GuildFeature] = _MISSING,
        description: str | None = _MISSING,
        premium_progress_bar_enabled: bool = _MISSING,
        safety_alerts_channel_id: int | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> Guild:
        """Edits the guild. This requires the :attr:`~mizuki.Permissions.MANAGE_GUILD` permission.

        All parameters to this method are optional and can be set to :obj:`None`.

        Parameters
        ----------
        name : :class:`str`
            The name of the guild.

        verification_level : :class:`~mizuki.GuildVerificationLevel`
            The verification level of the guild.

        default_message_notifications : :class:`~mizuki.GuildNotificationLevel`
            The notification level for the guild that is set by default for new joining users.

        explicit_content_filter : :class:`~mizuki.GuildExplicitContentLevel`
            Determines which members have the media they sent scanned for explicit content.

        afk_channel_id : :class:`int`
            The ID of the AFK Channel for the guild.

        afk_timeout : :class:`datetime.timedelta` | :class:`int`
            The AFK timeout, can be 1, 5, 15, 30, 60 minutes.

        icon : :class:`~mizuki.File` | :class:`str`
            The icon of the guild.

        splash : :class:`~mizuki.File` | :class:`str`
            The splash art for the guild.

        discovery_splash : :class:`~mizuki.File` | :class:`str`
            The discovery splash art for the guild.

        banner : :class:`~mizuki.File` | :class:`str`
            The banner of the guild.

        system_channel_id : :class:`int`
            The ID of the system channel of the guild. Welcome messages, boost messages, etc. are posted there.

        rules_channel_id : :class:`int`
            The ID of the rules channel of the guild.

        public_updates_channel_id : :class:`int`
            The ID of the channel where admins and mods recieve notices from Discord.

        preferred_locale : :class:`str`
            The preferred locale of the guild used in notices and discovery. Defaults to "en-US".

        features : :class:`list`[:class:`~mizuki.GuildFeature`]
            The enabled features for this guild.

        description : :class:`str`
            The description of the guild.

        premium_progress_bar_enabled : :class:`bool`
            Whether the guild's boost progress bar is enabled.

        safety_alerts_channel_id : :class:`int`
            The ID of the channel where the admins and mods recieve safety alerts from Discord.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are not allowed to edit that guild/setting.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.edit_guild(
            self.id,
            **{k: v for k, v in locals().items() if k != "self"},
        )

    async def fetch_channels(self) -> list[GuildChannel]:
        """Fetches the list of guild channels of a guild.

        Parameters
        ----------
        :class:`NotFound`
            Could not find the guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.fetch_channels(self.id)

    @overload
    async def create_channel(
        self,
        *,
        name: str,
        type: Literal[ChannelType.GUILD_TEXT] | None = _MISSING,
        topic: str | None = _MISSING,
        rate_limit_per_user: timedelta | int | None = _MISSING,
        position: int | None = _MISSING,
        permission_overwrites: list[ChannelPermissionOverwrite] | None = _MISSING,
        parent_id: int | None = _MISSING,
        nsfw: bool | None = _MISSING,
        default_auto_archive_duration: int | None = _MISSING,
        default_thread_rate_limit_per_user: timedelta | int | None = _MISSING,
        flags: ChannelFlags | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> GuildChannel: ...

    @overload
    async def create_channel(
        self,
        *,
        name: str,
        type: Literal[ChannelType.GUILD_ANNOUNCEMENT],
        topic: str | None = _MISSING,
        position: int | None = _MISSING,
        permission_overwrites: list[ChannelPermissionOverwrite] | None = _MISSING,
        parent_id: int | None = _MISSING,
        nsfw: bool | None = _MISSING,
        default_auto_archive_duration: int | None = _MISSING,
        default_thread_rate_limit_per_user: timedelta | int | None = _MISSING,
        flags: ChannelFlags | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> GuildChannel: ...

    @overload
    async def create_channel(
        self,
        *,
        name: str,
        type: Literal[ChannelType.GUILD_FORUM],
        topic: str | None = _MISSING,
        rate_limit_per_user: timedelta | int | None = _MISSING,
        position: int | None = _MISSING,
        permission_overwrites: list[ChannelPermissionOverwrite] | None = _MISSING,
        parent_id: int | None = _MISSING,
        nsfw: bool | None = _MISSING,
        default_auto_archive_duration: int | None = _MISSING,
        default_reaction_emoji: DefaultReaction | None = _MISSING,
        available_tags: list[PartialForumTag] | None = _MISSING,
        default_sort_order: SortOrderType | None = _MISSING,
        default_forum_layout: ForumLayoutType | None = _MISSING,
        default_thread_rate_limit_per_user: timedelta | int | None = _MISSING,
        flags: ChannelFlags | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> GuildChannel: ...

    @overload
    async def create_channel(
        self,
        *,
        name: str,
        type: Literal[ChannelType.GUILD_MEDIA],
        topic: str | None = _MISSING,
        rate_limit_per_user: timedelta | int | None = _MISSING,
        position: int | None = _MISSING,
        permission_overwrites: list[ChannelPermissionOverwrite] | None = _MISSING,
        parent_id: int | None = _MISSING,
        default_auto_archive_duration: int | None = _MISSING,
        default_reaction_emoji: DefaultReaction | None = _MISSING,
        available_tags: list[PartialForumTag] | None = _MISSING,
        default_sort_order: SortOrderType | None = _MISSING,
        default_thread_rate_limit_per_user: timedelta | int | None = _MISSING,
        flags: ChannelFlags | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> GuildChannel: ...

    @overload
    async def create_channel(
        self,
        *,
        name: str,
        type: Literal[ChannelType.GUILD_VOICE],
        bitrate: int | None = _MISSING,
        user_limit: int | None = _MISSING,
        rate_limit_per_user: timedelta | int | None = _MISSING,
        position: int | None = _MISSING,
        permission_overwrites: list[ChannelPermissionOverwrite] | None = _MISSING,
        parent_id: int | None = _MISSING,
        nsfw: bool | None = _MISSING,
        rtc_region: str | None = _MISSING,
        video_quality_mode: VideoQualityMode | None = _MISSING,
        flags: ChannelFlags | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> GuildChannel: ...

    @overload
    async def create_channel(
        self,
        *,
        name: str,
        type: Literal[ChannelType.GUILD_STAGE_VOICE],
        bitrate: int | None = _MISSING,
        user_limit: int | None = _MISSING,
        rate_limit_per_user: timedelta | int | None = _MISSING,
        position: int | None = _MISSING,
        permission_overwrites: list[ChannelPermissionOverwrite] | None = _MISSING,
        parent_id: int | None = _MISSING,
        nsfw: bool | None = _MISSING,
        rtc_region: str | None = _MISSING,
        video_quality_mode: VideoQualityMode | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> GuildChannel: ...

    async def create_channel(
        self,
        *,
        name: str,
        type: ChannelType | None = _MISSING,
        topic: str | None = _MISSING,
        bitrate: int | None = _MISSING,
        user_limit: int | None = _MISSING,
        rate_limit_per_user: timedelta | int | None = _MISSING,
        position: int | None = _MISSING,
        permission_overwrites: list[ChannelPermissionOverwrite] | None = _MISSING,
        parent_id: int | None = _MISSING,
        nsfw: bool | None = _MISSING,
        rtc_region: str | None = _MISSING,
        video_quality_mode: VideoQualityMode | None = _MISSING,
        default_auto_archive_duration: timedelta | int | None = _MISSING,
        default_reaction_emoji: DefaultReaction | None = _MISSING,
        available_tags: list[PartialForumTag] | None = _MISSING,
        default_sort_order: SortOrderType | None = _MISSING,
        default_forum_layout: ForumLayoutType | None = _MISSING,
        default_thread_rate_limit_per_user: timedelta | int | None = _MISSING,
        flags: ChannelFlags | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> GuildChannel:
        """Creates a channel in a guild.

        All parameters to this method besides `name` are optional and can be set to :obj:`None`.

        Parameters
        ----------
        name : :class:`str`
            The name of the channel (1-100 characters).

        type : :class:`~mizuki.ChannelType`
            The type of the channel.

        topic : :class:`str`
            The topic of the channel (0-1024 characters).

        bitrate : :class:`int`
            The bitrate (bits/second) of the voice/stage channel. Minimum 8000.

        user_limit : :class:`int`
            The user limit of a voice/stage channel.

        rate_limit_per_user : :class:`datetime.timedelta` | :class:`int`
            The amount of seconds an user has to wait before sending another message (0-21600 seconds).

        position : :class:`int`
            The sorting position of the channel. Channels with same position are sorted by IDs.

        permission_overwrites : :class:`list`[:class:`~mizuki.ChannelPermissionOverwrite`]
            The channel permissions to overwrite.

        parent_id : :class:`int`
            The ID of the category for a channel.

        nsfw : :class:`int`
            Whether the channel is age-restricted.

        rtc_region : :class:`str`
            The voice region ID of the voice or stage channel, automatic when set to `None`.

        video_quality_mode : :class:`~mizuki.VideoQualityMode`
            The camera video quality mode of the voice or stage channel.

        default_auto_archive_duration : :class:`timedelta` | :class:`int`
            The default duration that the client use for newly created threads to automatically archive the thread. :class:`int` is taken as minutes.

        default_reaction_emoji : :class:`~mizuki.DefaultReaction`
            The reaction that is shown by default on forum posts.

        available_tags : :class:`list`[:class:`~mizuki.PartialForumTag`]
            The tags that can be used in a forum or media channel.

        default_sort_order : :class:`~mizuki.SortOrderType`
            The default sort order used to order posts in a forum or media channel.

        default_forum_layout : :class:`~mizuki.ForumLayoutType`
            The default forum layout used to display in a forum channel.

        default_thread_rate_limit_per_user : :class:`int`
            The rate limit value that is copied over to newly-created threads.

        flags : :class:`~mizuki.ChannelFlags`
            The flags to set for the channel.

        audit_log_reason : :class:`str`
            The reason to show in audit log for the creation of this channel.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are not allowed to create that channel.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.create_channel(
            self.id,
            **{k: v for k, v in locals().items() if k != "self"},
        )

    async def edit_channel_positions(self, *changes: ChannelPositionChange) -> None:
        """Edit the positions of the channels in a guild.

        Parameters
        ----------
        *changes : :class:`~mizuki.ChannelPositionChange`
            The channel change objects.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are not allowed to edit the channel positions.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.edit_channel_positions(
            self.id, *changes
        )

    async def fetch_active_threads(
        self,
    ) -> tuple[list[ThreadChannel], list[ThreadMember]]:
        """Fetches the active threads in a guild.

        Returns the list of channel and the list of thread member for the bot if the bot is present in the thread.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are not allowed to fetch the threads of that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.fetch_active_threads(self.id)

    async def fetch_member(self, user_id: int) -> Member:
        """Fetch the member object of a guild member.

        Parameters
        ----------
        user_id : :class:`int`
            The ID of the target user.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild or an user with those IDs.

        :class:`Forbidden`
            You are not allowed to fetch the threads of that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.fetch_member(self.id, user_id)

    async def fetch_members(
        self,
        *,
        after: int = _MISSING,
        limit: int = _MISSING,
    ) -> list[Member]:
        """Fetch the list of members in the guild.

        Parameters
        ----------
        after : :class:`int`, optional
            To fetch the members after this ID.

        limit : :class:`int`, optional
            The max amount of members to return in a list (1-1000, defaults to 1).

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are not allowed to fetch the members of that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.fetch_members(
            self.id, after=after, limit=limit
        )

    async def search_members(
        self, query: str, *, limit: int = _MISSING
    ) -> list[Member]:
        """Search through guild members based on their nickname or username.

        Parameters
        ----------
        query : :class:`str`
            The query to match against the nickname or username.

        limit : :class:`int`, optional
            The max number of members to return (1-1000, defaults to 1).

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are not allowed to fetch the members of that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.search_members(
            self.id, query, limit=limit
        )

    async def modify_member(
        self,
        user_id: int,
        *,
        nick: str | None = _MISSING,
        roles: list[int] | None = _MISSING,
        mute: bool | None = _MISSING,
        deaf: bool | None = _MISSING,
        channel_id: int | None = _MISSING,
        communication_disabled_until: datetime | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> Member:
        """Edit a guild member.

        Parameters
        ----------
        user_id : :class:`int`
            The ID Of the target user.

        nick : :class:`str` | :obj:`None`, optional
            The string to change the nickname of the target to.

        roles : :class:`list`[:class:`int`] | :obj:`None`, optional
            The array of the ID of roles the user has.

        mute : :class:`bool` | :obj:`None`, optional
            Whether the member is muted in Voice Channels.

        deaf : :class:`bool` | :obj:`None`, optional
            Whether the member is deafened in Voice Channels.

        channel_id : :class:`bool` | :obj:`None`, optional
            The ID of the voice channel to move the member to, disconnects them if set to :obj:`None`.

        communication_disabled_until : :class:`datetime.datetime` | :obj:`None`, optional
            When the member's timeout will expire, max 28 days into the future.

        audit_log_reason : :class:`str`, optional
            The audit log reason for this change.

        Raises
        ------
        :class:`NotFound`
            Could not find that guild or user.

        :class:`Forbidden`
            You are not allowed to edit that user.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.modify_member(
            self.id,
            **{k: v for k, v in locals().values() if k != "self"},
        )

    async def timeout(
        self, user_id: int, *, until: datetime | timedelta | None
    ) -> Member:
        """Timeout/Mute a user from chatting.

        Parameters
        ----------
        user_id : :class:`int`
            The ID of the target user.

        until : :class:`datetime.datetime` | :class:`datetime.timedelta` | :obj:`None`
            To timeout the user until/for, maximum of 28 days in the future. Set to :obj:`None` to remove timeout.

        Raises
        ------
        :class:`NotFound`
            Could not find that guild or user.

        :class:`Forbidden`
            You cannot mute that user.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.timeout(self.id, user_id, until=until)

    async def modify_self_member(
        self,
        *,
        nick: str | None = _MISSING,
        banner: File | str | None = _MISSING,
        avatar: File | str | None = _MISSING,
        bio: str | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> Member:
        """Modify the bot's member in the guild.

        Parameters
        ----------
        nick : :class:`str`, optional
            The new nickname for the bot in that guild.

        banner : :class:`~mizuki.File` | :class:`str` | :obj:`None`, optional
            The new banner for the bot.

        avatar : :class:`~mizuki.File` | :class:`str` | :obj:`None`, optional
            The new avatar for the bot.

        bio : :class:`str` | :obj:`None`, optional
            The new bio for the bot.

        audit_log_reason : :class:`str`, optional
            The audit log reason to show for this change.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            Could not change that attribute about your profile.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.modify_self_member(
            self.id,
            nick=nick,
            banner=banner,
            avatar=avatar,
            bio=bio,
            audit_log_reason=audit_log_reason,
        )

    async def add_member_role(
        self,
        user_id: int,
        role_id: int,
        *,
        audit_log_reason: str = _MISSING,
    ) -> Member:
        """Add a role to a member.

        Parameters
        ----------
        user_id : :class:`int`
            The ID of the target member.

        role_id : :class:`int`
            The ID of the role to add.

        audit_log_reason : :class:`str`, optional
            The reason to show in audit log for this change.

        Parameters
        ----------
        :class:`NotFound`
            Could not find the guild, user or role.

        :class:`Forbidden`
            You are forbidden from editing roles or adding that role.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.add_member_role(
            self.id, user_id, role_id, audit_log_reason=audit_log_reason
        )

    async def remove_member_role(
        self,
        user_id: int,
        role_id: int,
        *,
        audit_log_reason: str = _MISSING,
    ) -> None:
        """Removes a role from a member.

        Parameters
        ----------
        user_id : :class:`int`
            The ID of the target member.

        role_id : :class:`int`
            The ID of the role to remove.

        audit_log_reason : :class:`str`, optional
            The reason to show in audit log for this change.

        Parameters
        ----------
        :class:`NotFound`
            Could not find the guild, user or role.

        :class:`Forbidden`
            You are forbidden from editing roles or removing that role.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.remove_member_role(
            self.id, user_id, role_id, audit_log_reason=audit_log_reason
        )

    async def remove_member(
        self, user_id: int, *, audit_log_reason: str = _MISSING
    ) -> None:
        """Remove/Kick a member from a guild.

        Parameters
        ----------
        user_id : :class:`int`
            The ID of the target member.

        audit_log_reason : :class:`str`, optional
            The reason to show in audit log for this removal.

        Parameters
        ----------
        :class:`NotFound`
            Could not find the guild or user.

        :class:`Forbidden`
            You are forbidden from removing that member.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.remove_member(
            self.id, user_id, audit_log_reason=audit_log_reason
        )

    @overload
    async def fetch_bans(
        self,
        *,
        limit: int = _MISSING,
        before: int,
    ) -> list[GuildBan]: ...

    @overload
    async def fetch_bans(
        self, *, limit: int = _MISSING, after: int
    ) -> list[GuildBan]: ...

    @overload
    async def fetch_bans(
        self,
        *,
        limit: int = _MISSING,
    ) -> list[GuildBan]: ...

    async def fetch_bans(
        self,
        *,
        limit: int = _MISSING,
        before: int = _MISSING,
        after: int = _MISSING,
    ) -> list[GuildBan]:
        """Fetch a list of bans in the guild.

        Parameters
        ----------
        limit : :class:`int`, optional
            The maximum amount of users to return (1-1000, defaults to 1000).

        before : :class:`int`, optional
            To return users before this user ID.

        after : :class:`int`, optional
            To return users after this user ID.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are not allowed to fetch the bans in that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        # pyrefly: ignore [no-matching-overload]
        return await self._state.managers.guilds.fetch_bans(
            self.id, limit=limit, before=before, after=after
        )

    async def fetch_ban(self, user_id: int) -> GuildBan:
        """Fetch a ban for the given user.

        Parameters
        ----------
        user_id : :class:`int`
            The ID of the target user.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild or a ban for that user.

        :class:`Forbidden`
            You are missing the required permissions to fetch a ban.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.fetch_ban(self.id, user_id)

    async def ban(
        self,
        user_id: int,
        *,
        delete_message: timedelta | int = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> None:
        """Create a new ban/Ban an user.

        Parameters
        ----------
        user_id : :class:`int`
            The ID of the target user.

        delete_message : :class:`datetime.timedelta` | :class:`int`, optional
            The amount of time to delete messages of, if an integer is provided it is treated as seconds.

        audit_log_reason : :class:`str`, optional
            The reason to show in the audit log for this ban.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild or user.

        :class:`Forbidden`
            You cannot ban that user.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.create_ban(
            self.id,
            user_id,
            delete_message=delete_message,
            audit_log_reason=audit_log_reason,
        )

    async def unban(self, user_id: int, *, audit_log_reason: str = _MISSING) -> None:
        """Remove a ban/Unban an user.

        Parameters
        ----------
        user_id : :class:`int`
            The ID of the target user.

        audit_log_reason : :class:`str`, optional
            The reason to show in the audit log for this unban.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild or user.

        :class:`Forbidden`
            You cannot unban that user.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.remove_ban(
            self.id, user_id, audit_log_reason=audit_log_reason
        )

    async def bulk_ban(
        self,
        user_ids: list[int],
        *,
        delete_message: timedelta | int = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> BulkBanResult:
        """Bulk a maximum of 200 users from a guild.

        Parameters
        ----------
        user_ids : :class:`list`[:class:`int`]
            The list of IDs of the users to ban.

        delete_message : :class:`datetime.timedelta` | :class:`int`, optional
            The amount of time to delete messages of, if an integer is provided it is treated as seconds.

        audit_log_reason : :class:`str`, optional
            The reason to show in the audit logs for this bulk ban.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are missing permissions to bulk ban in that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.guilds.bulk_ban(
            self.id,
            user_ids,
            delete_message=delete_message,
            audit_log_reason=audit_log_reason,
        )

    async def fetch_roles(self) -> list[Role]:
        """Fetch all the roles of a guild.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are missing permissions to fetch roles of that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.fetch_roles(self.id)

    async def fetch_role(self, role_id: int) -> Role:
        """Fetch all the roles of a guild.

        Parameters
        ----------
        role_id : :class:`int`
            The ID of the target role.

        Raises
        ------
        :class:`NotFound`
            Could not find that guild.

        :class:`Forbidden`
            You are missing permissions to fetch roles of that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.fetch_role(self.id, role_id)

    async def fetch_role_member_counts(self) -> dict[Snowflake, int]:
        """Fetch role count for every role in a guild.

        Returns a dictonary with role ID as keys and their member count as values.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are missing permissions to fetch roles of that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.fetch_role_member_counts(self.id)

    async def create_role(
        self,
        *,
        name: str = _MISSING,
        permissions: Permissions = _MISSING,
        colors: RoleColors = _MISSING,
        hoist: bool = _MISSING,
        icon: File | str | None = _MISSING,
        unicode_emoji: str | None = _MISSING,
        mentionable: bool = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> Role:
        """Create a new role in a guild.

        All parameters are optional.

        Parameters
        ----------
        name : :class:`int`
            The name of the new role, defaults to "new role".

        permissions : :class:`~mizuki.Permissions`
            The permissions for the new role.

        colors : :class:`~mizuki.RoleColors`
            The colors for the new role.

        hoist : :class:`bool`
            Whether the role is hoisted/shown separately in member lists.

        icon : :class:`~mizuki.File` | :class:`str` | :obj:`None`
            The icon of the new role.

        unicode_emoji : :class:`str` | :obj:`None`
            The related unicode emoji for the new role.

        mentionable : :class:`bool`
            Whether the role is mentionable.

        audit_log_reason : :class:`str`
            The reason to show in the audit log for the creation of this role.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are missing permissions to create roles in that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.create_role(
            self.id, **{k: v for k, v in locals().items() if k != "self"}
        )

    async def edit_role_positions(
        self,
        *changes: RolePositionChange,
        audit_log_reason: str = _MISSING,
    ) -> list[Role]:
        """Edit role positions in a guild.

        Parameters
        ----------
        *changes : :class:`~mizuki.RolePositionChange`
            The changes to be made to the role positions.

        audit_log_reason : :class:`str`, optional
            The reason to show in the audit log for this change.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are missing permissions to edit role positions in that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.edit_role_positions(
            self.id, *changes, audit_log_reason=audit_log_reason
        )

    async def edit_role(
        self,
        role_id: int,
        *,
        name: str | None = _MISSING,
        permissions: Permissions | None = _MISSING,
        colors: RoleColors | None = _MISSING,
        hoist: bool | None = _MISSING,
        icon: File | str | None = _MISSING,
        unicode_emoji: str | None = _MISSING,
        mentionable: bool | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> Role:
        """Edit a role in a guild.

        All parameters are optional.

        Parameters
        ----------
        role_id : :class:`int`
            The ID of the target role.

        name : :class:`int`
            The name of the role.

        permissions : :class:`~mizuki.Permissions`
            The permissions for the role.

        colors : :class:`~mizuki.RoleColors`
            The colors for the role.

        hoist : :class:`bool`
            Whether the role is hoisted/shown separately in member lists.

        icon : :class:`~mizuki.File` | :class:`str` | :obj:`None`
            The icon of the role.

        unicode_emoji : :class:`str` | :obj:`None`
            The related unicode emoji for new role.

        mentionable : :class:`bool`
            Whether the role is mentionable.

        audit_log_reason : :class:`str`
            The reason to show in the audit log for the editing of this role.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are missing permissions to edit roles in that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.edit_role(
            self.id, **{k: v for k, v in locals().items() if k != "self"}
        )

    async def delete_role(
        self, role_id: int, *, audit_log_reason: str = _MISSING
    ) -> None:
        """Delete a role in a guild.

        Parameters
        ----------
        role_id : :class:`int`
            The ID of the target role.

        audit_log_reason : :class:`str`
            The reason to show in the audit log for the editing of this role.

        Raises
        ------
        :class:`NotFound`
            Could not find the guild.

        :class:`Forbidden`
            You are missing permissions to delete that role in that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.roles.delete_role(
            self.id, role_id, audit_log_reason=audit_log_reason
        )

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
