from typing import cast

from mizuki.flags import ChannelFlags
from mizuki.http import Path
from mizuki._utils import _MISSING, assign_val_dict, mtd

from mizuki.managers._types import BaseManager
from mizuki.objects.channel import (
    PartialForumTag,
    ThreadChannel,
    GuildChannel,
    Channel,
    parse_channel_payload
)
from mizuki.enums.channel import (
    ChannelType,
    ForumLayoutType,
    SortOrderType,
    VideoQualityMode
)
from mizuki.objects.emoji import DefaultReaction
from mizuki.objects.permissions import ChannelPermissionOverwrite

__all__ = (
    "ChannelManager",
)

class ChannelManager(BaseManager):
    """
    Manager used to fetch :class:`Channel <mizuki.objects.channel.Channel>` objects.
    """

    __slots__ = ()

    def get(self, channel_id: int) -> Channel | None:
        """
        Attempts to fetch a :class:`Channel <mizuki.objects.channel.Channel>` from the internal cache of the bot.

        Parameters
        ----------
        channel_id: :class:`int`
            The channel_id of the channel to fetch.

        Returns
        -------
        :class:`Channel <mizuki.objects.channel.Channel>`
            The Channel object recieved from the cache.

        :class:`None`
            The Channel could not be found in the cache.
        """
        return self._cache_storage.get_channel(channel_id)

    async def fetch(self, channel_id: int) -> Channel:
        """
        Attempts to fetch a :class:`Channel <mizuki.objects.channel.Channel>` from the Discord API.

        Parameters
        ----------
        channel_id: :class:`int`
            The channel_id of the channel to fetch.

        Raises
        ------
        :class:`NotFound`
            Could not find an channel with that ID.

        :class:`Forbidden`
            You are not allowed to fetch that channel.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_channels(
            parse_channel_payload(await self._state.http.request(
                Path(
                    "GET",
                    "channels/{channel_id}",
                    channel_id=channel_id
            )))
        )

    async def get_or_fetch(self, channel_id: int) -> Channel:
        """
        A couroutine function that attempts to fetch a :class:`Channel <mizuki.objects.channel.Channel>` from internal cache and if not present, makes an API call to discord.

        Parameters
        ----------
        channel_id: :class:`int`
            The channel_id of the channel to fetch.

        Raises
        ------
        :class:`NotFound`
            Could not find an channel with that ID.

        :class:`Forbidden`
            You are not allowed to fetch that channel.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self.get(channel_id) or await self.fetch(channel_id)

    async def edit(
        self, channel_id: int,
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
        flags: ChannelFlags = _MISSING,
        available_tags: list[PartialForumTag] = _MISSING,
        default_reaction_emoji: DefaultReaction | None = _MISSING,
        default_thread_rate_limit_per_user: int = _MISSING,
        default_sort_order: SortOrderType | None = _MISSING,
        default_forum_layout: ForumLayoutType = _MISSING,
        archived: bool = _MISSING,
        auto_archive_duration: int = _MISSING,
        invitable: bool = _MISSING,
        locked: bool = _MISSING,
        applied_tags: list[int] = _MISSING
    ) -> Channel:
        """
        Modifies a channel.

        Requires the :attr:`MANAGE_CHANNELS <mizuki.objects.permissions.Permissions.MANAGE_CHANNELS>` for a guild channel or :attr:`MANAGE_THREADS <mizuki.objects.permissions.Permissions.MANAGE_THREADS>` for a thread. Additionally, requires :attr:`MANAGE_ROLES <mizuki.objects.permissions.Permissions.MANAGE_ROLES>` if modifying the permissions.

        .. note::

            All parameters besides ``channel_id`` are optional.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel.

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
            The ID of the nww parent category for a channel.

        rtc_region : :class:`str` | :class:`None`
            The voice region of the channel. Sets to automatic when ``None`` is provided.

        video_quality_mode : :class:`VideoQualityMode <mizuki.enums.channel.VideoQualityMode>` | :class:`None`
            The camera video quality mode of the channel.

        default_auto_archive_duration : :class:`int`
            The default auto archive duration that the clients use for newly created threads in the channel, in minutes.

        flags : :class:`ChannelFlags <mizuki.flags.ChannelFlags>`
            The flags for the channel.

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

        archived : :class:`bool`
            Whether the thread is archived.

        auto_archive_duration : :class:`int`
            The minutes of inactivity after which the thread will be archived.

        locked : :class:`bool`
            Whether the thread is locked.

        invitable : :class:`bool`
            Whether non-moderators can add other non-moderators to this thread. Only available on private threads.

        applied_tags : list[:class:`int`]
            The IDs of tags applied to a thread in a :attr:`GUILD_FORUM <mizuki.enums.channel.ChannelType.GUILD_FORUM>` and :attr:`GUILD_MEDIA <mizuki.enums.channel.ChannelType.GUILD_MEDIA>` channel. Max 5.

        Raises
        ------
        :class:`NotFound`
            Could not find an channel with that ID.

        :class:`Forbidden`
            You are not allowed to edit that channel.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_channels(
            parse_channel_payload(await self._state.http.request(
                Path(
                    "PATCH",
                    "channels/{channel_id}",
                    channel_id=channel_id
                ),
                json=assign_val_dict(
                    {}, _MISSING,
                    name=name,
                    type=(
                        type.value
                        if type is not _MISSING
                        else _MISSING
                    ),
                    position=position,
                    topic=topic,
                    nsfw=nsfw,
                    rate_limit_per_user=rate_limit_per_user,
                    bitrate=bitrate,
                    user_limit=user_limit,
                    permission_overwrites=(
                        [p._to_dict() for p in permission_overwrites]
                        if permission_overwrites not in (_MISSING, None)
                        else permission_overwrites
                    ),
                    parent_id=parent_id,
                    rtc_region=rtc_region,
                    video_quality_mode=(
                        video_quality_mode.value
                        if video_quality_mode not in (_MISSING, None)
                        else video_quality_mode
                    ),
                    default_auto_archive_duration=default_auto_archive_duration,
                    flags=(
                        flags.value
                        if flags is not _MISSING
                        else _MISSING
                    ),
                    available_tags=(
                        [t._to_dict() for t in available_tags]
                        if available_tags is not _MISSING
                        else _MISSING
                    ),
                    default_reaction_emoji=mtd(default_reaction_emoji),
                    default_thread_rate_limit_per_user=default_thread_rate_limit_per_user,
                    default_sort_order=(
                        default_sort_order.value
                        if default_sort_order not in (_MISSING, None)
                        else default_sort_order
                    ),
                    default_forum_layout=(
                        default_forum_layout.value
                        if default_forum_layout is not _MISSING
                        else default_forum_layout
                    ),
                    archived=archived,
                    auto_archive_duration=auto_archive_duration,
                    invitable=invitable,
                    locked=locked,
                    applied_tags=applied_tags
                )
            ))
    )

    async def edit_guild_channel(
        self, channel_id: int,
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
        default_forum_layout: ForumLayoutType = _MISSING
    ) -> GuildChannel:
        """
        Modifies a channel.

        Requires the :attr:`MANAGE_CHANNELS <mizuki.objects.permissions.Permissions.MANAGE_CHANNELS>`. Additionally, requires :attr:`MANAGE_ROLES <mizuki.objects.permissions.Permissions.MANAGE_ROLES>` if modifying the permissions.

        .. note::

            All parameters besides ``channel_id`` are optional.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel.

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
        if (
            require_tag is not _MISSING
            or hide_media_download_options is not _MISSING
        ):
            flags = ChannelFlags(0)
            if require_tag: flags |= ChannelFlags.REQUIRE_TAG
            if hide_media_download_options: flags |= ChannelFlags.HIDE_MEDIA_DOWNLOAD_OPTIONS
        else:
            flags = _MISSING

        return cast(GuildChannel, await self.edit(
            channel_id,
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
            flags=flags,
            available_tags=available_tags,
            default_reaction_emoji=default_reaction_emoji,
            default_thread_rate_limit_per_user=default_thread_rate_limit_per_user,
            default_sort_order=default_sort_order,
            default_forum_layout=default_forum_layout
        ))

    async def edit_thread(
        self, thread_id: int,
        *,
        name: str = _MISSING,
        archived: bool = _MISSING,
        auto_archive_duration: int = _MISSING,
        rate_limit_per_user: int | None = _MISSING,
        locked: bool = _MISSING,
        invitable: bool = _MISSING,
        pinned: bool = _MISSING,
        applied_tags: list[int] = _MISSING
    ) -> ThreadChannel:
        """
        Modifies a thread.

        Requires the :attr:`MANAGE_THREADS <mizuki.objects.permissions.Permissions.MANAGE_THREADS>`.

        .. note::

            All parameters besides ``channel_id`` are optional.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel.

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
        return cast(ThreadChannel, await self.edit(
            thread_id,
            name=name,
            archived=archived,
            auto_archive_duration=auto_archive_duration,
            invitable=invitable,
            rate_limit_per_user=rate_limit_per_user,
            locked=locked,
            flags=(
                (
                    ChannelFlags.PINNED
                    if pinned
                    else ChannelFlags(0)
                ) if pinned is not _MISSING
                else _MISSING
            ),
            applied_tags=applied_tags
        ))

    async def set_voice_status(
        self, channel_id: int,
        *, status: str | None
    ) -> None:
        """
        Set a voice channel's status.

        Requires the :attr:`SET_VOICE_CHANNEL_STATUS <mizuki.objects.permissions.Permissions.SET_VOICE_CHANNEL_STATUS>` permission, and additionally the :attr:`MANAGE_CHANNELS <mizuki.objects.permissions.Permissions.MANAGE_CHANNELS>` permission if the current user is not connected to the voice channel.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the voice channel.

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
        await self._state.http.request(
            Path(
                "PUT",
                "channels/{channel_id}/voice-status",
                channel_id=channel_id
            ),
            json={"status": status}
        )

    async def delete(self, channel_id: int) -> Channel:
        """
        Deletes a channel or closes a private channel.

        Requires the :attr:`MANAGE_CHANNELS <mizuki.objects.permissions.Permissions.MANAGE_CHANNELS>` for a guild channel or :attr:`MANAGE_THREADS <mizuki.objects.permissions.Permissions.MANAGE_THREADS>` for a thread.

        Deleting a category does not delete its child channels.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel.

        Raises
        ------
        :class:`NotFound`
            Could not find an channel with that ID.

        :class:`Forbidden`
            You are not allowed to delete that channel.

        :class:`HTTPException`
            A HTTP error occured.
        """
        channel = parse_channel_payload(await self._state.http.request(
            Path(
                "DELETE",
                "channels/{channel_id}",
                channel_id=channel_id
            )
        ))

        self._cache_storage.remove_channel(channel_id)
        return channel

    async def edit_permissions(
        self, channel_id: int,
        *, overwrite: ChannelPermissionOverwrite
    ) -> None:
        """
        Edits permissions for a role or a user for a channel.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel.

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
        await self._state.http.request(
            Path(
                "PUT",
                "channels/{channel_id}/permissions/{overwrite_id}",
                channel_id=channel_id,
                overwrite_id=overwrite.id
            ),
            json=assign_val_dict(
                {},
                allow=overwrite.allow.value,
                deny=overwrite.deny.value,
                type=overwrite.type.value
            )
        )
