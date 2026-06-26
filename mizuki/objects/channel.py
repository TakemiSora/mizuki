from __future__ import annotations
from datetime import datetime, timedelta
from typing import Literal, Self, cast, overload, TYPE_CHECKING

from mizuki._utils import assign_val, scls, sint, siso
from mizuki.enums.channel import (
    ChannelType,
    ForumLayoutType,
    SortOrderType,
    VideoQualityMode,
)
from mizuki.errors import UnknownChannelType
from mizuki.flags import ChannelFlags
from mizuki.objects.member import Member
from mizuki.objects.permissions import ChannelPermissionOverwrite, Permissions
from mizuki.objects.snowflake import Snowflake
from mizuki.objects.user import User
from mizuki.payloads.channel import (
    BaseChannelPayload,
    BasePublicChannelPayload,
    ChannelMentionPayload,
    ForumTagPayload,
    GuildChannelPayload,
    PartialForumTagPayload,
    PartialGuildChannelPayload,
    PartialThreadPayload,
    PrivateChannelPayload,
    ThreadMemberPayload,
    ThreadMetaDataPayload,
    ThreadPayload,
)

if TYPE_CHECKING:
    from mizuki.state import ConnectionState

__all__ = (
    "ThreadMetaData",
    "ThreadMember",
    "PartialForumTag",
    "ForumTag",
    "GuildChannel",
    "ThreadChannel",
    "PrivateChannel",
    "PartialGuildChannel",
    "PartialThreadChannel",
    "ChannelMention",
    "Channel"
)

class ThreadMetaData:
    """
    Represents the metadata of a thread.
    """

    archived: bool
    "Represents if the thread is archived."

    auto_archive_duration: timedelta
    "The amount of time before the thread is auto-archived. Can only be 60, 1440, 4320, 10080 in terms of minutes."

    archive_timestamp: datetime
    "Represents when the thread's archive status was last changed, used for calculating recent activity"

    locked: bool
    "Represents if the thread is locked."

    invitable: bool
    "Whether non-moderators can add other non-moderators to a thread, only available on Private Threads."

    create_timestamp: datetime | None
    "Represents when the thread was created. Will be ``None`` for threads older than 2022-01-09."

    __slots__ = (
        "archived",
        "auto_archive_duration",
        "archive_timestamp",
        "locked",
        "invitable",
        "create_timestamp"
    )

    def __init__(self, data: ThreadMetaDataPayload):
        self.archived = data["archived"]
        self.auto_archive_duration = timedelta(minutes=data["auto_archive_duration"])
        self.archive_timestamp = datetime.fromisoformat(data["archive_timestamp"])
        self.locked = data["locked"]
        self.invitable = data.get("invitable", False)
        self.create_timestamp = siso(data.get("create_timestamp"))

class ThreadMember:
    """
    Represents information about an user that has joined a thread.
    """

    id: Snowflake | None
    "The ID of the :class:`Thread <mizuki.objects.channel.ThreadChannel>`. Omitted in :attr:`GUILD_CREATE <mizuki.enums.event_dispatch.Event.GUILD_CREATE>`."

    user_id: Snowflake | None
    "The ID of the :class:`User <mizuki.objects.user.User>`. Omitted in :attr:`GUILD_CREATE <mizuki.enums.event_dispatch.Event.GUILD_CREATE>`."

    join_timestamp: datetime
    "Time the user last joined the thread."

    notifications: bool
    "Represents if the :class:`User <mizuki.objects.user.User>` has notifications enabled."

    member: Member | None
    "The Member Object for the user in the :class:`Guild <mizuki.objects.guild.Guild>`. Omitted in :attr:`GUILD_CREATE <mizuki.enums.event_dispatch.Event.GUILD_CREATE>`."

    __slots__ = (
        "id",
        "user_id",
        "join_timestamp",
        "notifications",
        "member"
    )

    def __init__(self, data: ThreadMemberPayload, guild_id: int | None = None, user_id: int | None = None, *, state: ConnectionState):
        self.id = Snowflake._from_str(data.get("id"))
        self.user_id = Snowflake._from_str(data.get("user_id"))
        self.join_timestamp = datetime.fromisoformat(data["join_timestamp"])
        self.notifications = bool(data["flags"])
        if guild_id and user_id:
            self.member = scls(Member, data.get("member"), guild_id=guild_id, user_id=user_id, state=state)
        else:
            self.member = None

class PartialForumTag:
    """
    Represents a partial Forum Tag object to be passed for editing the available tags of a channel.
    """
    name: str
    "The name of the tag. (0-20 characters long)"

    __slots__ = (
        "name",
    )

    def __init__(self, data: PartialForumTagPayload):
        self.name = data["name"]

    def _to_dict(self) -> PartialForumTagPayload:
        return PartialForumTagPayload(name=self.name)

    @classmethod
    def new(cls, *, name: str) -> Self:
        """
        Creates a new instance of a partial Forum Tag.

        Parameters
        ----------
        name : :class:`str`
            The name of the tag.
        """
        return assign_val(cls.__new__(cls), name=name)

class ForumTag(PartialForumTag):
    """
    Represents a Forum Tag which can be applied to Channels of types :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>`.

    .. note::

        Atleast one of :attr:`emoji_id <mizuki.objects.channel.ForumTag.emoji_id>` and :attr:`emoji_name <mizuki.objects.channel.ForumTag.emoji_name>` will always be present.
    """

    id: Snowflake
    "The ID of the Tag."

    moderated: bool
    "Whether this Tag can only be added to or removed from valid ChannelType by a member with the :attr:`MANAGE_THREADS <mizuki.objects.permissions.Permissions.MANAGE_THREADS>` permission."

    emoji_id: Snowflake | None
    "The ID of a :class:`Guild <mizuki.objects.guild.Guild>`’s custom emoji."

    emoji_name: str | None
    "The unicode character of the emoji."

    __slots__ = (
        "id",
        "moderated",
        "emoji_id",
        "emoji_name"
    )

    def __init__(self, data: ForumTagPayload):
        super().__init__(data)
        self.id = Snowflake(data["id"])
        self.moderated = data["moderated"]
        self.emoji_id = Snowflake._from_str(data["emoji_id"])
        self.emoji_name = data["emoji_name"]

    def _to_dict(self) -> ForumTagPayload:
        return ForumTagPayload(
            id=str(self.id),
            name=self.name,
            moderated=self.moderated,
            emoji_id=str(self.emoji_id),
            emoji_name=self.emoji_name
        )

class BaseChannel:

    id: Snowflake
    "The ID of the Channel."

    last_message_id: Snowflake | None
    "The ID of the last message (or :class:`Thread <mizuki.objects.channel.ThreadChannel>` for :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>`) that was sent in that channel. May or may not point to a valid message."

    flags: ChannelFlags
    "The flags of the Channel."

    last_pin_timestamp: datetime | None
    "The timestamp when the last pinned message was pinned. May be ``None`` if no messages are pinned."

    __slots__ = (
        "_state",
        "id",
        "last_message_id",
        "flags",
        "last_pin_timestamp"
    )

    def __init__(self, data: BaseChannelPayload, *, state: ConnectionState):
        self._state = state
        self.id = Snowflake(data["id"])
        self.last_message_id = Snowflake._from_str(data.get("last_message_id"))
        self.flags = ChannelFlags(data["flags"])
        self.last_pin_timestamp = siso(data.get("last_pin_timestamp"))

    def __eq__(self, obj: object) -> bool:
        if isinstance(obj, self.__class__):
            return self.id == obj.id
        return NotImplemented

    def __hash__(self) -> int:
        return self.id

    @property
    def created_at(self) -> datetime:
        """
        The timestamp at which the Channel was created.

        Returns
        -------
        :class:`datetime <datetime.datetime>`
        """
        return self.id.created_at

class BasePublicChannel(BaseChannel):
    guild_id: Snowflake
    "The :class:`Guild <mizuki.objects.guild.Guild>` ID of the Channel."

    name: str
    "The name of the channel"

    rate_limit_per_user: int | None
    "The amount of time an user has to wait before sending a message (Slowmode). Bots remain unaffected."

    permissions: Permissions | None
    "Computed permissions for the invoking user in the channel, including overwrites, only included when part of the :class:`Resolved Data <mizuki.objects.interaction.ResolvedData>` received on an :class:`Interaction <mizuki.objects.interaction.Interaction>`. This does not include implicit permissions, which may need to be checked separately"

    __slots__ = (
        "guild_id",
        "name",
        "parent_id",
        "rate_limit_per_user",
        "permissions",
    )

    def __init__(self, data: BasePublicChannelPayload, guild_id: int | None = None, *, state: ConnectionState):
        super().__init__(data, state=state)
        resolved_guild_id = data.get("guild_id") or str(guild_id)
        assert resolved_guild_id is not None, "A PublicChannel object formed without any guild_id."
        self.guild_id = Snowflake(resolved_guild_id)
        self.name = data["name"]
        self.parent_id = Snowflake._from_str(data.get("parent_id"))
        self.rate_limit_per_user = data.get("rate_limit_per_user")
        self.permissions = scls(Permissions, sint(data.get("permissions")))

class GuildChannel(BasePublicChannel):
    """
    Represents a Channel/Category in a Guild.

    Channel Types
    -------------
    - :attr:`GUILD_TEXT <mizuki.enums.channel.ChannelType.GUILD_TEXT>`
    - :attr:`GUILD_VOICE <mizuki.enums.channel.ChannelType.GUILD_VOICE>`
    - :attr:`GUILD_CATEGORY <mizuki.enums.channel.ChannelType.GUILD_CATEGORY>`
    - :attr:`GUILD_ANNOUNCEMENT <mizuki.enums.channel.ChannelType.GUILD_ANNOUNCEMENT>`
    - :attr:`GUILD_STAGE_VOICE <mizuki.enums.channel.ChannelType.GUILD_STAGE_VOICE>`
    - :attr:`GUILD_DIRECTORY <mizuki.enums.channel.ChannelType.GUILD_DIRECTORY>`
    - :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>`
    - :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>`
    """

    type: ChannelType
    "The type of this Channel."

    parent_id: Snowflake | None
    "The ID of the category (channel of :attr:`GUILD_CATEGORY <mizuki.enums.channel.ChannelType.GUILD_CATEGORY>`), if any."

    topic: str | None
    "The topic of the channel. 0-4096 character limit for :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>`, 0-1024 for all others."

    default_auto_archive_duration: timedelta | None
    "The default amount of time before a newly created :class:`thread <mizuki.objects.channel.ThreadChannel>` is auto-archived. Can only be 60, 1440, 4320, 10080 in terms of minutes."

    default_thread_rate_limit_per_user: int | None
    "The default rate limit for new :class:`threads <mizuki.objects.channel.ThreadChannel>`. Does not live-update with the channel's rate limit. Bots remain unaffected."

    position: int | None
    "Sorting position of the channel (Channels with the same position are sorted by id)"

    permission_overwrites: list[ChannelPermissionOverwrite]
    "Explicit permission overwrites for member and roles."

    nsfw: bool
    "Whether the channel is NSFW."

    available_tags: list[ForumTag]
    "The list of tags that can be used in :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>` channels."

    default_sort_order: SortOrderType | None
    "Default sortorder used when posting in a :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>` channel. ``None`` indicates that the setting hasn't been set by an admin."

    default_forum_layout: ForumLayoutType | None
    "The default ForumLayout used to display posts in :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` channels."

    bitrate: int | None
    "The bitrate in bits/second for a voice channel. (:attr:`GUILD_VOICE <mizuki.enums.channel.ChannelType.GUILD_VOICE>` and :attr:`GUILD_STAGE_VOICE <mizuki.enums.channel.ChannelType.GUILD_STAGE_VOICE>`)."

    user_limit: int | None
    "The User Limit for a voice channel. (:attr:`GUILD_VOICE <mizuki.enums.channel.ChannelType.GUILD_VOICE>` and :attr:`GUILD_STAGE_VOICE <mizuki.enums.channel.ChannelType.GUILD_STAGE_VOICE>`)."

    rtc_region: str | None
    "The RTC Region ID for a voice channel. (:attr:`GUILD_VOICE <mizuki.enums.channel.ChannelType.GUILD_VOICE>` and :attr:`GUILD_STAGE_VOICE <mizuki.enums.channel.ChannelType.GUILD_STAGE_VOICE>`)."

    video_quality_mode: VideoQualityMode
    "The VideoQualityMode of the channel, default :attr:`AUTO <mizuki.enums.channel.VideoQualityMode.AUTO>`."

    __slots__ = (
        "type",
        "topic",
        "default_auto_archive_duration",
        "default_thread_rate_limit_per_user",
        "position",
        "permission_overwrites",
        "nsfw",
        "available_tags",
        "default_sort_order",
        "default_forum_layout",
        "bitrate",
        "user_limit",
        "rtc_region",
        "video_quality_mode",
    )

    def __init__(self, data: GuildChannelPayload, guild_id: int | None = None, *, state: ConnectionState):
        super().__init__(data, guild_id, state=state)
        self.type = ChannelType(data["type"])
        self.topic = data.get("topic")
        self.default_auto_archive_duration = scls(timedelta, data.get("default_auto_archive_duration"))
        self.default_thread_rate_limit_per_user = data.get("default_thread_rate_limit_per_user")
        self.position = data["position"]
        self.permission_overwrites = [ChannelPermissionOverwrite(p) for p in data.get("permission_overwrites", [])]
        self.nsfw = data.get("nsfw", False)
        self.available_tags = [ForumTag(f) for f in data.get("available_tags", [])]
        self.default_sort_order = scls(SortOrderType, data.get("default_sort_order"))
        self.default_forum_layout = scls(ForumLayoutType, data.get("default_forum_layout"))
        self.bitrate = data.get("bitrate")
        self.user_limit = data.get("user_limit")
        self.rtc_region = data.get("rtc_region")
        self.video_quality_mode = VideoQualityMode(data.get("video_quality_mode", 1))

class ThreadChannel(BasePublicChannel):
    """
    Represents a Thread Channel in a Guild.

    Channel Types
    -------------
    - :attr:`ANNOUNCEMENT_THREAD <mizuki.enums.channel.ChannelType.ANNOUNCEMENT_THREAD>`
    - :attr:`PUBLIC_THREAD <mizuki.enums.channel.ChannelType.PUBLIC_THREAD>`
    - :attr:`PRIVATE_THREAD <mizuki.enums.channel.ChannelType.PRIVATE_THREAD>`
    """

    type: ChannelType
    "The type of this channel."

    owner_id: Snowflake
    "The owner of this thread."

    thread_metadata: ThreadMetaData
    "Metadata of the thread."

    message_count: int
    "The amount of messages present in this thread, is inaccurate when above 50 for threads made before July 1, 2022."

    member_count: int
    "The amount of members in this thread. Stops counting at 50."

    total_message_sent: int
    "The total amount of messages ever sent in this thread."

    applied_tags: list[Snowflake]
    "The tags applied to a thead in a :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>` channel."

    __slots__ = (
        "type",
        "owner_id",
        "thread_metadata",
        "message_count",
        "member_count",
        "total_message_sent",
        "applied_tags",
    )

    def __init__(self, data: ThreadPayload, guild_id: int | None = None, *, state: ConnectionState):
        super().__init__(data, guild_id, state=state)
        self.type = ChannelType(data["type"])
        self.owner_id = Snowflake(data["owner_id"])
        self.thread_metadata = ThreadMetaData(data["thread_metadata"])
        self.message_count = data["message_count"]
        self.member_count = data["member_count"]
        self.total_message_sent = data["total_message_sent"]
        self.applied_tags = [Snowflake(s) for s in data.get("applied_tags", [])]

class PrivateChannel(BaseChannel):
    """
    Represents a private (DM) channel.
    """

    recipients: list[User]
    "The recipients or the members of the channel."

    type: ChannelType
    "The ChannelType of this Channel. Always :attr:`DM <mizuki.enums.channel.ChannelType.DM>`."

    __slots__ = (
        "recipients",
        "type"
    )

    def __init__(self, data: PrivateChannelPayload, *, state: ConnectionState):
        super().__init__(data, state=state)
        self.recipients = [User(u, state=state) for u in data["recipients"]]
        self.type = ChannelType(data["type"])

class PartialGuildChannel(BasePublicChannel):
    """
    Represents a Partial Channel/Category in a Guild.

    Channel Types
    -------------
    - :attr:`GUILD_TEXT <mizuki.enums.channel.ChannelType.GUILD_TEXT>`
    - :attr:`GUILD_VOICE <mizuki.enums.channel.ChannelType.GUILD_VOICE>`
    - :attr:`GUILD_CATEGORY <mizuki.enums.channel.ChannelType.GUILD_CATEGORY>`
    - :attr:`GUILD_ANNOUNCEMENT <mizuki.enums.channel.ChannelType.GUILD_ANNOUNCEMENT>`
    - :attr:`GUILD_STAGE_VOICE <mizuki.enums.channel.ChannelType.GUILD_STAGE_VOICE>`
    - :attr:`GUILD_DIRECTORY <mizuki.enums.channel.ChannelType.GUILD_DIRECTORY>`
    - :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>`
    - :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>`
    """

    type: ChannelType
    "The type of this Channel."

    parent_id: Snowflake | None
    "The ID of the category (channel of :attr:`GUILD_CATEGORY <mizuki.enums.channel.ChannelType.GUILD_CATEGORY>`), if any."

    topic: str | None
    "The topic of the channel. 0-4096 character limit for :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>`, 0-1024 for all others."

    position: int | None
    "Sorting position of the channel (Channels with the same position are sorted by id)"

    nsfw: bool
    "Whether the channel is NSFW."

    __slots__ = (
        "type",
        "topic",
        "position",
        "nsfw"
    )

    def __init__(self, data: PartialGuildChannelPayload, guild_id: int | None, *, state: ConnectionState):
        super().__init__(data, guild_id, state=state)
        self.type = ChannelType(data["type"])
        self.topic = data.get("topic")
        self.position = data["position"]
        self.nsfw = data.get("nsfw", False)

class PartialThreadChannel(BasePublicChannel):
    """
    Represents a Thread Channel in a Guild.

    Channel Types
    -------------
    - :attr:`ANNOUNCEMENT_THREAD <mizuki.enums.channel.ChannelType.ANNOUNCEMENT_THREAD>`
    - :attr:`PUBLIC_THREAD <mizuki.enums.channel.ChannelType.PUBLIC_THREAD>`
    - :attr:`PRIVATE_THREAD <mizuki.enums.channel.ChannelType.PRIVATE_THREAD>`
    """

    type: ChannelType
    "The type of this channel."

    thread_metadata: ThreadMetaData
    "Metadata of the thread."

    __slots__ = (
        "type",
        "thread_metadata"
    )

    def __init__(self, data: PartialThreadPayload, guild_id: int | None = None, *, state: ConnectionState):
        super().__init__(data, guild_id, state=state)
        self.type = ChannelType(data["type"])
        self.thread_metadata = ThreadMetaData(data["thread_metadata"])

class ChannelMention:
    """
    Represents a minimal channel object for :attr:`Message.mention_channels <mizuki.objects.message.Message.mention_channels>`.
    """

    id: Snowflake
    "The ID of the channel."

    guild_id: Snowflake
    "The :class:`Guild <mizuki.objects.guild.Guild>` ID of the channel."

    type: ChannelType
    "The type of the channel."

    name: str
    "The name of the channel."

    __slots__ = (
        "id",
        "guild_id",
        "type",
        "name"
    )

    def __init__(self, data: ChannelMentionPayload):
        self.id = Snowflake(data["id"])
        self.guild_id = Snowflake(data["guild_id"])
        self.type = ChannelType(data["type"])
        self.name = data["name"]

@overload
def parse_channel_payload(
    data: GuildChannelPayload,
    guild_id: int | None = None,
    *, partial: Literal[False] = False,
    state: ConnectionState
) -> GuildChannel: ...

@overload
def parse_channel_payload(
    data: ThreadPayload,
    guild_id: int | None = None,
    *, partial: Literal[False] = False,
    state: ConnectionState
) -> ThreadChannel: ...

@overload
def parse_channel_payload(
    data: PrivateChannelPayload,
    *, partial: bool = False,
    state: ConnectionState
) -> PrivateChannel: ...

@overload
def parse_channel_payload(
    data: PartialGuildChannelPayload,
    guild_id: int | None = None,
    *, partial: Literal[True],
    state: ConnectionState
) -> PartialGuildChannel: ...

@overload
def parse_channel_payload(
    data: PartialThreadPayload,
    guild_id: int | None = None,
    *, partial: Literal[True],
    state: ConnectionState
) -> PartialThreadChannel: ...

def parse_channel_payload(
    data: GuildChannelPayload | ThreadPayload | PrivateChannelPayload | PartialGuildChannelPayload | PartialThreadPayload,
    guild_id: int | None = None,
    *, partial: bool = False,
    state: ConnectionState
) -> GuildChannel | ThreadChannel | PrivateChannel | PartialGuildChannel | PartialThreadChannel:
    match ChannelType(data["type"]):
        case ChannelType.DM:
            return PrivateChannel(cast(PrivateChannelPayload, data), state=state)
        case (
            ChannelType.ANNOUNCEMENT_THREAD
            | ChannelType.PUBLIC_THREAD
            | ChannelType.PRIVATE_THREAD
        ):
            return (
                PartialThreadChannel(cast(PartialThreadPayload, data), guild_id, state=state)
                if partial else ThreadChannel(cast(ThreadPayload, data), guild_id, state=state)
            )
        case (
            ChannelType.GUILD_TEXT
            | ChannelType.GUILD_VOICE
            | ChannelType.GUILD_CATEGORY
            | ChannelType.GUILD_ANNOUNCEMENT
            | ChannelType.GUILD_STAGE_VOICE
            | ChannelType.GUILD_FORUM
            | ChannelType.GUILD_DIRECTORY
            | ChannelType.GUILD_FORUM
            | ChannelType.GUILD_MEDIA
        ):
            return (
                PartialGuildChannel(cast(PartialGuildChannelPayload, data), guild_id, state=state)
                if partial else GuildChannel(cast(GuildChannelPayload, data), guild_id, state=state)
            )
        case _:
            raise UnknownChannelType(f"Received unknown channel type '{data["type"]}'")

type Channel = ThreadChannel | PrivateChannel | GuildChannel
"This is only a type hint for all channel types, not an object."