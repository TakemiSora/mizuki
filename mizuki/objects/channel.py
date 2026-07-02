from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Literal, Self, cast, overload

from mizuki._utils import _MISSING, assign_val, scls, sint, siso
from mizuki.enums.channel import (
    ChannelType,
    ForumLayoutType,
    SortOrderType,
    VideoQualityMode,
)
from mizuki.errors import UnknownChannelType
from mizuki.flags import ChannelFlags, MessageFlags
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
    from mizuki.file import File
    from mizuki.objects.embed import Embed
    from mizuki.objects.emoji import DefaultReaction
    from mizuki.objects.message import AllowedMentions, Message, MessageReference
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
    "Channel",
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
        "create_timestamp",
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

    __slots__ = ("id", "user_id", "join_timestamp", "notifications", "member")

    def __init__(
        self,
        data: ThreadMemberPayload,
        guild_id: int | None = None,
        user_id: int | None = None,
        *,
        state: ConnectionState,
    ):
        self.id = Snowflake._from_str(data.get("id"))
        self.user_id = Snowflake._from_str(data.get("user_id"))
        self.join_timestamp = datetime.fromisoformat(data["join_timestamp"])
        self.notifications = bool(data["flags"])
        if guild_id and user_id:
            self.member = scls(
                Member,
                data.get("member"),
                guild_id=guild_id,
                user_id=user_id,
                state=state,
            )
        else:
            self.member = None


class PartialForumTag:
    """
    Represents a partial Forum Tag object to be passed for editing the available tags of a channel.
    """

    name: str
    "The name of the tag. (0-20 characters long)"

    __slots__ = ("name",)

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

    __slots__ = ("id", "moderated", "emoji_id", "emoji_name")

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
            emoji_name=self.emoji_name,
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

    __slots__ = ("_state", "id", "last_message_id", "flags", "last_pin_timestamp")

    def __init__(self, data: BaseChannelPayload, *, state: ConnectionState):
        self._state = state
        self._update(data)

    def _update(self, data: BaseChannelPayload):
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

    async def send(
        self,
        content: str = _MISSING,
        *,
        tts: bool = _MISSING,
        embeds: list[Embed] = _MISSING,
        allowed_mentions: AllowedMentions = _MISSING,
        message_reference: MessageReference = _MISSING,
        files: list[File] = _MISSING,
        sticker_ids: list[int] = _MISSING,
        flags: MessageFlags = _MISSING,
    ) -> Message:
        """
        Creates a new message in the specified channel.

        .. note::

            At least one of, ``content``, ``embeds``, ``sticker_ids``, ``files`` must be provided. For forwarding, only ``message_reference`` must be provided.

        Parameters
        ----------
        content : :class:`str`
            The content of the message.

        tts : :class:`bool`
            Whether TTS is enabled for the message.

        embeds : list[:class:`Embed <mizuki.objects.embed.Embed>`]
            The list of embeds to send along the message.

        allowed_mentions : :class:`AllowedMentions <mizuki.objects.message.AllowedMentions>`
            The AllowedMentions object that dictates whether user, role or everyone pings are enabled.

        files : list[:class:`File <mizuki.file.File>`]
            The files to upload with the message.

        message_reference : :class:`MessageReference <mizuki.objects.message.MessageReference>`
            The reference message for the new message, if any

        sticker_ids : list[:class:`int`]
            The Guild Stickers to send with the message. Max 3.

        flags : :class:`MessageFlags <mizuki.flags.MessageFlags>`
            The MessageFlags of the new message.

        Raises
        ------
        :class:`NotFound`
            The channel you tried to send to doesn't exist.

        :class:`Forbidden`
            You are not allowed to send the message. You may be missing a specific permission.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return await self._state.managers.messages.create(
            self.id,
            content=content,
            tts=tts,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            message_reference=message_reference,
            files=files,
            sticker_ids=sticker_ids,
            flags=flags,
        )


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

    def __init__(
        self,
        data: BasePublicChannelPayload,
        guild_id: int | None = None,
        *,
        state: ConnectionState,
    ):
        self._state = state
        self._update(data, guild_id)

    def _update(self, data: BasePublicChannelPayload, guild_id: int | None) -> None:
        assert (
            resolved_guild_id := (data.get("guild_id") or str(guild_id))
        ) is not None, "A PublicChannel object formed without any guild ID."

        super()._update(data)
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

    def __init__(
        self,
        data: GuildChannelPayload,
        guild_id: int | None = None,
        *,
        state: ConnectionState,
    ):
        self._state = state
        self._update(data, guild_id)

    def _update(self, data: GuildChannelPayload, guild_id: int | None):
        super()._update(data, guild_id)

        self.type = ChannelType(data["type"])
        self.topic = data.get("topic")
        self.default_auto_archive_duration = scls(
            timedelta, data.get("default_auto_archive_duration")
        )
        self.default_thread_rate_limit_per_user = data.get(
            "default_thread_rate_limit_per_user"
        )
        self.position = data["position"]
        self.permission_overwrites = [
            ChannelPermissionOverwrite(p) for p in data.get("permission_overwrites", [])
        ]
        self.nsfw = data.get("nsfw", False)
        self.available_tags = [ForumTag(f) for f in data.get("available_tags", [])]
        self.default_sort_order = scls(SortOrderType, data.get("default_sort_order"))
        self.default_forum_layout = scls(
            ForumLayoutType, data.get("default_forum_layout")
        )
        self.bitrate = data.get("bitrate")
        self.user_limit = data.get("user_limit")
        self.rtc_region = data.get("rtc_region")
        self.video_quality_mode = VideoQualityMode(data.get("video_quality_mode", 1))

    async def edit(
        self,
        *,
        name: str = _MISSING,
        type: ChannelType = _MISSING,
        position: int | None = _MISSING,
        topic: str | None = _MISSING,
        nsfw: bool | None = _MISSING,
        rate_limit_per_user: int | None = _MISSING,
        bitrate: int | None = _MISSING,
        user_limit: int | None = _MISSING,
        permission_overwrites: list[ChannelPermissionOverwrite] | None = _MISSING,
        parent_id: int | None = _MISSING,
        rtc_region: str | None = _MISSING,
        video_quality_mode: VideoQualityMode | None = _MISSING,
        default_auto_archive_duration: int | None = _MISSING,
        require_tag: bool = _MISSING,
        hide_media_download_options: bool = _MISSING,
        available_tags: list[PartialForumTag] = _MISSING,
        default_reaction_emoji: DefaultReaction | None = _MISSING,
        default_thread_rate_limit_per_user: int = _MISSING,
        default_sort_order: SortOrderType | None = _MISSING,
        default_forum_layout: ForumLayoutType = _MISSING,
    ) -> GuildChannel:
        """
        Modifies a channel.

        Requires the :attr:`MANAGE_CHANNELS <mizuki.objects.permissions.Permissions.MANAGE_CHANNELS>`. Additionally, requires :attr:`MANAGE_ROLES <mizuki.objects.permissions.Permissions.MANAGE_ROLES>` if modifying the permissions.

        .. note::

            All parameters are optional.

        Parameters
        ----------
        name : :class:`str`
            The name of the channel. (1-100 characters)

        type : :class:`ChannelType <mizuki.enums.channel.ChannelType>`
            The new type of the channel. Only the conversion between a :attr:`GUILD_TEXT <mizuki.enums.channel.ChannelType.GUILD_TEXT>` channel and a :attr:`GUILD_ANNOUNCEMENT <mizuki.enums.channel.ChannelType.GUILD_ANNOUNCEMENT>` channel is supported.

        position : :class:`int` | :class:`None`
            The position of the channel.

        topic : :class:`str` | :class:`None`
            The topic of the channel. 0-4096 character limit for :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>`, 0-1024 for all others.

        nsfw : :class:`bool` | :class:`None`
            Whether the channel is NSFW.

        rate_limit_per_user : :class:`int` | :class:`None`
            The amount of seconds the user has to wait before sending a message again. (0-21600 seconds)

        bitrate : :class:`int` | :class:`None`
            The bitrate of the voice or stage channel. Minimum 8000.

        user_limit : :class:`int` | :class:`None`
            The user limit for the voice or the stage channel. 0 for no limit. Max 99 for voice channels and 10,000 for stage channels.

        permission_overwrites : list[:class:`ChannelPermissionOverwrite <mizuki.objects.permissions.ChannelPermissionOverwrite>`] | :class:`None`
            The channel or category-specific permissions.

        parent_id : :class:`int` | :class:`None`
            The ID of the new parent category for a channel.

        rtc_region : :class:`str` | :class:`None`
            The voice region of the channel. Sets to automatic when ``None`` is provided.

        video_quality_mode : :class:`VideoQualityMode <mizuki.enums.channel.VideoQualityMode>` | :class:`None`
            The camera video quality mode of the channel.

        default_auto_archive_duration : :class:`int`
            The default auto archive duration that the clients use for newly created threads in the channel, in minutes.

        require_tag : :class:`bool`
            Whether the :attr:`REQUIRE_TAG <mizuki.flags.ChannelFlags.REQUIRE_TAG>` is added to the flags.

        hide_media_download_options : :class:`bool`
            Whether the :attr:`HIDE_MEDIA_DOWNLOAD_OPTIONS <mizuki.flags.ChannelFlags.HIDE_MEDIA_DOWNLOAD_OPTIONS>` is added to the flags.

        available_tags : list[:class:`PartialForumTag <mizuki.objects.channel.PartialForumTag>`]
            The set of tags that can be used in a :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>` channel. Max 20.

        default_reaction_emoji : :class:`DefaultReaction <mizuki.objects.emoji.DefaultReaction>`
            The default emoji reaction shown in the add reaction button on threads.

        default_thread_rate_limit_per_user : :class:`int`
            The rate limit per user to set on newly created threads. Only synced on creation of thread.

        default_sort_order : :class:`SortOrderType <mizuki.enums.channel.SortOrderType>`
            The default sort order used for posts in a :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>` channel.

        default_forum_layout : :class:`ForumLayoutType <mizuki.enums.channel.ForumLayoutType>`
            The default forum layout used in :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` channel.

        Raises
        ------
        :class:`NotFound`
            Could not find an channel with that ID.

        :class:`Forbidden`
            You are not allowed to edit that channel.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.channels.edit_guild_channel(
            self.id,
            name=name,
            type=type,
            position=position,
            topic=topic,
            nsfw=nsfw,
            rate_limit_per_user=rate_limit_per_user,
            bitrate=bitrate,
            user_limit=user_limit,
            permission_overwrites=permission_overwrites,
            parent_id=parent_id,
            rtc_region=rtc_region,
            video_quality_mode=video_quality_mode,
            default_auto_archive_duration=default_auto_archive_duration,
            require_tag=require_tag,
            hide_media_download_options=hide_media_download_options,
            available_tags=available_tags,
            default_reaction_emoji=default_reaction_emoji,
            default_thread_rate_limit_per_user=default_thread_rate_limit_per_user,
            default_sort_order=default_sort_order,
            default_forum_layout=default_forum_layout,
            to_update=self,
        )

    async def set_voice_status(self, status: str | None) -> None:
        """
        Set a voice channel's status.

        Requires the :attr:`SET_VOICE_CHANNEL_STATUS <mizuki.objects.permissions.Permissions.SET_VOICE_CHANNEL_STATUS>` permission, and additionally the :attr:`MANAGE_CHANNELS <mizuki.objects.permissions.Permissions.MANAGE_CHANNELS>` permission if the current user is not connected to the voice channel.

        Parameters
        ----------
        status : :class:`str` | :class:`None`
            The new voice channel status. Max 500 characters.

        Raises
        ------
        :class:`NotFound`
            Could not find an channel with that ID.

        :class:`Forbidden`
            You are not allowed to edit that voice status.

        :class:`HTTPException`
            A HTTP error occured.
        """
        await self._state.managers.channels.set_voice_status(self.id, status=status)

    async def delete(self) -> None:
        """
        Deletes a channel.

        Requires the :attr:`MANAGE_CHANNELS <mizuki.objects.permissions.Permissions.MANAGE_CHANNELS>`.

        Deleting a category does not delete its child channels.

        Raises
        ------
        :class:`NotFound`
            Could not find an channel with that ID.

        :class:`Forbidden`
            You are not allowed to delete that channel.

        :class:`HTTPException`
            A HTTP error occured.
        """
        await self._state.managers.channels.delete(self.id)

    async def edit_permissions(self, overwrite: ChannelPermissionOverwrite) -> None:
        """
        Edits permissions for a role or a user for a channel.

        Parameters
        ----------
        overwrite : :class:`ChannelPermissionOverwrite <mizuki.objects.permissions.ChannelPermissionOverwrite>`
            The overwrite object to overwrite with.

        Raises
        ------
        :class:`NotFound`
            Could not find an channel with that ID or the role or the user with the ID in the overwrite object.

        :class:`Forbidden`
            You are not allowed to edit permissions for that channel and/or role or user.

        :class:`HTTPException`
            A HTTP error occured.
        """
        await self._state.managers.channels.edit_permissions(
            self.id, overwrite=overwrite
        )

    async def delete_messages(self, message_ids: list[int]) -> None:
        return await self._state.managers.messages.bulk_delete(
            channel_id=self.id, message_ids=message_ids
        )


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

    def __init__(
        self,
        data: ThreadPayload,
        guild_id: int | None = None,
        *,
        state: ConnectionState,
    ):
        self._state = state
        self._update(data, guild_id)

    def _update(self, data: ThreadPayload, guild_id: int | None):
        super()._update(data, guild_id)

        self.type = ChannelType(data["type"])
        self.owner_id = Snowflake(data["owner_id"])
        self.thread_metadata = ThreadMetaData(data["thread_metadata"])
        self.message_count = data["message_count"]
        self.member_count = data["member_count"]
        self.total_message_sent = data["total_message_sent"]
        self.applied_tags = [Snowflake(s) for s in data.get("applied_tags", [])]

    async def edit(
        self,
        *,
        name: str = _MISSING,
        archived: bool = _MISSING,
        auto_archive_duration: int = _MISSING,
        rate_limit_per_user: int | None = _MISSING,
        locked: bool = _MISSING,
        invitable: bool = _MISSING,
        pinned: bool = _MISSING,
        applied_tags: list[int] = _MISSING,
    ) -> ThreadChannel:
        """
        Modifies a thread.

        Requires the :attr:`MANAGE_THREADS <mizuki.objects.permissions.Permissions.MANAGE_THREADS>`.

        .. note::

            All parameters are optional.

        Parameters
        ----------
        name : :class:`str`
            The name of the channel. (1-100 characters)

        archived : :class:`bool`
            Whether the thread is archived.

        auto_archive_duration : :class:`int`
            The minutes of inactivity after which the thread will be archived.

        rate_limit_per_user : :class:`int` | :class:`None`
            The amount of seconds the user has to wait before sending a message again. (0-21600 seconds)

        locked : :class:`bool`
            Whether the thread is locked.

        invitable : :class:`bool`
            Whether non-moderators can add other non-moderators to this thread. Only available on private htewads.

        pinned : :class:`bool`
            Whether the :attr:`PINNED <mizuki.flags.ChannelFlags.PINNED>` is added to the flags.

        applied_tags : list[:class:`int`]
            The IDs of tags applied to a thread in a :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>` channel. Max 5.

        Raises
        ------
        :class:`NotFound`
            Could not find an channel with that ID.

        :class:`Forbidden`
            You are not allowed to edit that thread.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self._state.managers.channels.edit_thread(
            self.id,
            name=name,
            archived=archived,
            auto_archive_duration=auto_archive_duration,
            invitable=invitable,
            rate_limit_per_user=rate_limit_per_user,
            locked=locked,
            pinned=pinned,
            applied_tags=applied_tags,
            to_update=self,
        )

    async def delete(self) -> None:
        """
        Deletes a thread.

        Requires the :attr:`MANAGE_THREADS <mizuki.objects.permissions.Permissions.MANAGE_THREADS>`

        Raises
        ------
        :class:`NotFound`
            Could not find an thread with that ID.

        :class:`Forbidden`
            You are not allowed to delete that thread.

        :class:`HTTPException`
            A HTTP error occured.
        """
        await self._state.managers.channels.delete(self.id)


class PrivateChannel(BaseChannel):
    """
    Represents a private (DM) channel.
    """

    recipients: list[User]
    "The recipients or the members of the channel."

    type: ChannelType
    "The ChannelType of this Channel. Always :attr:`DM <mizuki.enums.channel.ChannelType.DM>`."

    __slots__ = ("recipients", "type")

    def __init__(self, data: PrivateChannelPayload, *, state: ConnectionState):
        self._state = state
        self._update(data, state=state)

    def _update(self, data: PrivateChannelPayload, *, state: ConnectionState):
        super()._update(data)

        self.recipients = [User(u, state=state) for u in data["recipients"]]
        self.type = ChannelType(data["type"])

    async def close(self) -> None:
        """
        Closes a private channel.

        Raises
        ------
        :class:`NotFound`
            Could not find an channel with that ID.

        :class:`HTTPException`
            A HTTP error occured.
        """
        await self._state.managers.channels.delete(self.id)


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

    __slots__ = ("type", "topic", "position", "nsfw")

    def __init__(
        self,
        data: PartialGuildChannelPayload,
        guild_id: int | None,
        *,
        state: ConnectionState,
    ):
        self._state = state
        self._update(data, guild_id)

    def _update(self, data: PartialGuildChannelPayload, guild_id: int | None):
        super()._update(data, guild_id)

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

    __slots__ = ("type", "thread_metadata")

    def __init__(
        self,
        data: PartialThreadPayload,
        guild_id: int | None = None,
        *,
        state: ConnectionState,
    ):
        self._state = state
        self._update(data, guild_id)

    def _update(self, data: PartialThreadPayload, guild_id: int | None):
        super()._update(data, guild_id)

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

    __slots__ = ("id", "guild_id", "type", "name")

    def __init__(self, data: ChannelMentionPayload):
        self.id = Snowflake(data["id"])
        self.guild_id = Snowflake(data["guild_id"])
        self.type = ChannelType(data["type"])
        self.name = data["name"]


@overload
def parse_channel_payload(
    data: GuildChannelPayload,
    guild_id: int | None = None,
    *,
    partial: Literal[False] = False,
    state: ConnectionState,
) -> GuildChannel: ...


@overload
def parse_channel_payload(
    data: ThreadPayload,
    guild_id: int | None = None,
    *,
    partial: Literal[False] = False,
    state: ConnectionState,
) -> ThreadChannel: ...


@overload
def parse_channel_payload(
    data: PrivateChannelPayload, *, partial: bool = False, state: ConnectionState
) -> PrivateChannel: ...


@overload
def parse_channel_payload(
    data: PartialGuildChannelPayload,
    guild_id: int | None = None,
    *,
    partial: Literal[True],
    state: ConnectionState,
) -> PartialGuildChannel: ...


@overload
def parse_channel_payload(
    data: PartialThreadPayload,
    guild_id: int | None = None,
    *,
    partial: Literal[True],
    state: ConnectionState,
) -> PartialThreadChannel: ...


def parse_channel_payload(
    data: GuildChannelPayload
    | ThreadPayload
    | PrivateChannelPayload
    | PartialGuildChannelPayload
    | PartialThreadPayload,
    guild_id: int | None = None,
    *,
    partial: bool = False,
    state: ConnectionState,
) -> (
    GuildChannel
    | ThreadChannel
    | PrivateChannel
    | PartialGuildChannel
    | PartialThreadChannel
):
    match ChannelType(data["type"]):
        case ChannelType.DM:
            return PrivateChannel(cast(PrivateChannelPayload, data), state=state)
        case (
            ChannelType.ANNOUNCEMENT_THREAD
            | ChannelType.PUBLIC_THREAD
            | ChannelType.PRIVATE_THREAD
        ):
            return (
                PartialThreadChannel(
                    cast(PartialThreadPayload, data), guild_id, state=state
                )
                if partial
                else ThreadChannel(cast(ThreadPayload, data), guild_id, state=state)
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
                PartialGuildChannel(
                    cast(PartialGuildChannelPayload, data), guild_id, state=state
                )
                if partial
                else GuildChannel(
                    cast(GuildChannelPayload, data), guild_id, state=state
                )
            )
        case _:
            raise UnknownChannelType(f"Received unknown channel type '{data['type']}'")


type Channel = ThreadChannel | PrivateChannel | GuildChannel
"This is only a type hint for all channel types, not an object."
