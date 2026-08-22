from datetime import datetime, timedelta
from typing import Literal, cast, overload

from mizuki._utils import _MISSING, assign_val_dict, maybe_iter, mgetattr, mtd
from mizuki.enums.channel import (
    ChannelType,
    ForumLayoutType,
    SortOrderType,
    VideoQualityMode,
)
from mizuki.enums.guild import (
    GuildExplicitContentLevel,
    GuildFeature,
    GuildNotificationLevel,
    GuildVerificationLevel,
)
from mizuki.file import File, maybe_encode_file
from mizuki.flags import ChannelFlags, SystemChannelFlags
from mizuki.http import Path
from mizuki.managers._types import BaseManager
from mizuki.objects.channel import (
    GuildChannel,
    PartialForumTag,
    ThreadChannel,
    ThreadMember,
    parse_channel_payload,
)
from mizuki.objects.emoji import DefaultReaction
from mizuki.objects.guild import (
    BulkBanResult,
    ChannelPositionChange,
    Guild,
    GuildBan,
    GuildPreview,
)
from mizuki.objects.member import Member
from mizuki.objects.permissions import ChannelPermissionOverwrite, Permissions
from mizuki.objects.role import Role, RoleColors, RolePositionChange
from mizuki.payloads.channel import GuildChannelPayload
from mizuki.payloads.role import RolePayload

__all__ = ("GuildManager",)


class GuildManager(BaseManager):
    """Manager used to fetch :class:`Guild <mizuki.objects.guild.Guild>` objects."""

    __slots__ = ()

    def get(self, guild_id: int) -> Guild | None:
        """Attempts to fetch a :class:`Guild <mizuki.objects.guild.Guild>` from the internal cache of the bot.

        Parameters
        ----------
        guild_id : :class:`int`
            The guild_id of the guild to fetch.
        """
        return self._cache_storage.get_guild(guild_id)

    async def fetch(self, guild_id: int, with_counts: bool = True) -> Guild:
        """Attempts to fetch a :class:`Guild <mizuki.objects.guild.Guild>` from the Discord API.

        Parameters
        ----------
        guild_id : :class:`int`
            The guild_id of the guild to fetch.

        Raises
        ------
        :class:`NotFound`
            Could not find an guild with that ID.

        :class:`Forbidden`
            You are not allowed to fetch that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_guilds(
            Guild(
                await self._state.http.request(
                    Path("GET", "guilds/{guild_id}", guild_id=guild_id),
                    params={"with_counts": str(with_counts)},
                ),
                state=self._state,
            )
        )

    async def get_or_fetch(self, guild_id: int) -> Guild:
        """A couroutine function that attempts to fetch a :class:`Guild <mizuki.objects.guild.Guild>` from internal cache and if not present, makes an API call to discord.

        Parameters
        ----------
        guild_id : :class:`int`
            The guild_id of the guild to fetch.

        Raises
        ------
        :class:`NotFound`
            Could not find an guild with that ID.

        :class:`Forbidden`
            You are not allowed to fetch that guild.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self.get(guild_id) or await self.fetch(guild_id)

    async def fetch_guild_preview(self, guild_id: int) -> GuildPreview:
        """Returns the guild preview object for the given ID.

        The guild must be discoverable if the bot is not present in the guild.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the guild to fetch the preview of.

        Raises
        ------
        :class:`NotFound`
            Could not find a guild with that ID.

        :class:`Forbidden`
            You are not allowed to fetch that preview.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return GuildPreview(
            await self._state.http.request(
                Path("GET", "guilds/{guild_id}/preview", guild_id=guild_id),
            ),
            state=self._state,
        )

    async def edit_guild(
        self,
        guild_id: int,
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
        """Edits the guild. This requires the :attr:`MANAGE_GUILD <mizuki.objects.permissions.Permissions.MANAGE_GUILD>` permission.

        All parameters to this method besides name are optional and can be set to `None`.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the guild to edit.

        name : :class:`str`
            The name of the guild.

        verification_level : :class:`GuildVerificationLevel <mizuki.enums.guild.GuildVerificationLevel>`
            The verification level of the guild.

        default_message_notifications : :class:`GuildNotificationLevel <mizuki.enums.guild.GuildNotificationLevel>`
            The notification level for the guild that is set by default for new joining users.

        explicit_content_filter : :class:`GuildExplicitContentLevel`
            Determines which members have the media they sent scanned for explicit content.

        afk_channel_id : :class:`int`
            The ID of the AFK Channel for the guild.

        afk_timeout : :class:`datetime.timedelta` | :class:`int`
            The AFK timeout, can be 1, 5, 15, 30, 60 minutes.

        icon : :class:`File <mizuki.file.File>` | :class:`str`
            The icon of the guild.

        splash : class:`File <mizuki.file.File>` | :class:`str`
            The splash art for the guild.

        discovery_splash : :class:`File <mizuki.file.File>` | :class:`str`
            The discovery splash art for the guild.

        banner : :class:`File <mizuki.file.File>` | :class:`str`
            The banner of the guild.

        system_channel_id : :class:`int`
            The ID of the system channel of the guild. Welcome messages, boost messages, etc. are posted there.

        rules_channel_id : :class:`int`
            The ID of the rules channel of the guild.

        public_updates_channel_id : :class:`int`
            The ID of the channel where admins and mods recieve notices from Discord.

        preferred_locale : :class:`str`
            The preferred locale of the guild used in notices and discovery. Defaults to "en-US".

        features : list[:class:`GuildFeature <mizuki.enums.guild.GuildFeature>`]
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
            Could not find a guild with that ID.

        :class:`Forbidden`
            You are not allowed to edit that guild/setting.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_guilds(
            Guild(
                await self._state.http.request(
                    Path("PATCH", "guilds/{guild_id}", guild_id=guild_id),
                    json=assign_val_dict(
                        {},
                        _MISSING,
                        name=name,
                        verification_level=mgetattr(verification_level, "value"),
                        default_message_notifications=mgetattr(
                            default_message_notifications, "value"
                        ),
                        explicit_content_filter=mgetattr(
                            explicit_content_filter, "value"
                        ),
                        afk_channel_id=afk_channel_id,
                        afk_timeout=(
                            afk_timeout.seconds
                            if isinstance(afk_timeout, timedelta)
                            else afk_timeout
                        ),
                        icon=await maybe_encode_file(icon),
                        splash=await maybe_encode_file(splash),
                        discovery_splash=await maybe_encode_file(discovery_splash),
                        banner=await maybe_encode_file(banner),
                        system_channel_id=system_channel_id,
                        system_channel_flags=mgetattr(system_channel_flags, "value"),
                        rules_channel_id=rules_channel_id,
                        public_updates_channel_id=public_updates_channel_id,
                        preferred_locale=preferred_locale,
                        features=maybe_iter(features, method=lambda x: x.value),
                        description=description,
                        premium_progress_bar_enabled=premium_progress_bar_enabled,
                        safety_alerts_channel_id=safety_alerts_channel_id,
                    ),
                    audit_log_reason=audit_log_reason,
                ),
                state=self._state,
            )
        )

    async def fetch_channels(self, guild_id: int) -> list[GuildChannel]:
        """Fetches the list of guild channels of a guild.

        Parameters
        ----------
        :class:`NotFound`
            Could not find a guild with that ID.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return [
            GuildChannel(d, guild_id=guild_id, state=self._state)
            for d in cast(
                list[GuildChannelPayload],
                await self._state.http.request(
                    Path("GET", "guilds/{guild_id}/channels", guild_id=guild_id)
                ),
            )
        ]

    @overload
    async def create_channel(
        self,
        guild_id: int,
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
        guild_id: int,
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
        guild_id: int,
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
        guild_id: int,
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
        guild_id: int,
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
        guild_id: int,
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
        guild_id: int,
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

        All parameters to this method besides, guild_id and name are optional and nullable.

        Parameters
        ----------
        guild_id : :class:`int`
            The ID of the target guild.

        name : :class:`str`
            The name of the channel (1-100 characters).

        type : :class:`ChannelType <mizuki.enums.channel.ChannelType>`
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

        permission_overwrites : list[:class:`ChannelPermissionOverwrite <mizuki.objects.channel.ChannelPermissionOverwrite>`]
            The channel permissions to overwrite.

        parent_id : :class:`int`
            The ID of the category for a channel.

        nsfw : :class:`int`
            Whether the channel is age-restricted.

        rtc_region : :class:`str`
            The voice region ID of the voice or stage channel, automatic when set to `None`.

        video_quality_mode : :class:`VideoQualityMode <mizuki.enums.channel.VideoQualityMode>`
            The camera video quality mode of the voice or stage channel.

        default_auto_archive_duration : :class:`timedelta` | :class:`int`
            The default duration that the client use for newly created threads to automatically archive the thread. :class:`int` is taken as minutes.

        default_reaction_emoji : :class:`DefaultReaction <mizuki.objects.emoji.DefaultReaction>`
            The reaction that is shown by default on forum posts.

        available_tags : list[:class:`PartialForumTag <mizuki.objects.channel.PartialForumTag>`]
            The tags that can be used in a forum or media channel.

        default_sort_order : :class:`SortOrderType <mizuki.enums.channel.SortOrderType>`
            The default sort order used to order posts in a forum or media channel.

        default_forum_layout : :class:`ForumLayoutType <mizuki.enums.channel.ForumLayoutType>`
            The default forum layout used to display in a forum channel.

        default_thread_rate_limit_per_user : :class:`int`
            The rate limit value that is copied over to newly-created threads.
        """
        return self._cache_storage.update_channels(
            parse_channel_payload(
                await self._state.http.request(
                    Path("POST", "guilds/{guild_id}/channels", guild_id=guild_id),
                    json=assign_val_dict(
                        {"name": name},
                        _MISSING,
                        type=getattr(type, "value", type),
                        topic=topic,
                        bitrate=bitrate,
                        user_limit=user_limit,
                        rate_limit_per_user=(
                            rate_limit_per_user.seconds
                            if isinstance(rate_limit_per_user, timedelta)
                            else rate_limit_per_user
                        ),
                        position=position,
                        permission_overwrites=maybe_iter(permission_overwrites),
                        parent_id=parent_id,
                        nsfw=nsfw,
                        rtc_region=rtc_region,
                        video_quality_mode=getattr(
                            video_quality_mode, "value", video_quality_mode
                        ),
                        default_auto_archive_duration=(
                            default_auto_archive_duration.seconds // 60
                            if isinstance(default_auto_archive_duration, timedelta)
                            else default_auto_archive_duration
                        ),
                        default_reaction_emoji=mtd(default_reaction_emoji),
                        available_tags=maybe_iter(available_tags),
                        default_sort_order=getattr(
                            default_sort_order, "value", default_sort_order
                        ),
                        default_forum_layout=getattr(
                            default_forum_layout, "value", default_forum_layout
                        ),
                        default_thread_rate_limit_per_user=(
                            default_thread_rate_limit_per_user.seconds
                            if isinstance(default_thread_rate_limit_per_user, timedelta)
                            else default_thread_rate_limit_per_user
                        ),
                        flags=getattr(flags, "value", flags),
                    ),
                    audit_log_reason=audit_log_reason,
                ),
                state=self._state,
            )
        )

    async def edit_channel_positions(
        self, guild_id: int, *changes: ChannelPositionChange
    ) -> None:
        await self._state.http.request(
            Path("PATCH", "guilds/{guild_id}/channels", guild_id=guild_id),
            json=maybe_iter(changes),
        )

    async def fetch_active_threads(
        self, guild_id: int
    ) -> tuple[list[ThreadChannel], list[ThreadMember]]:
        resp = await self._state.http.request(
            Path("GET", "guilds/{guild_id}/threads/active", guild_id=guild_id),
        )

        threads = [
            self._cache_storage.update_channels(
                ThreadChannel(t, guild_id=guild_id, state=self._state)
            )
            for t in resp["threads"]
        ]

        members = [
            ThreadMember(m, guild_id=guild_id, state=self._state)
            for m in resp["members"]
        ]

        return threads, members

    async def fetch_guild_member(self, guild_id: int, user_id: int) -> Member:
        return Member(
            await self._state.http.request(
                Path(
                    "GET",
                    "guilds/{guild_id}/members/{user_id}",
                    guild_id=guild_id,
                    user_id=user_id,
                )
            ),
            guild_id=guild_id,
            user_id=user_id,
            state=self._state,
        )

    async def fetch_guild_members(
        self,
        guild_id: int,
        *,
        after: int = _MISSING,
        limit: int = _MISSING,
    ) -> list[Member]:
        return [
            Member(m, guild_id=guild_id, state=self._state)
            for m in await self._state.http.request(
                Path(
                    "GET",
                    "guilds/{guild_id}/members",
                    guild_id=guild_id,
                ),
                params=assign_val_dict({}, _MISSING, after=after, limit=limit),
            )
        ]

    async def search_members(
        self, guild_id: int, query: str, *, limit: int = _MISSING
    ) -> list[Member]:
        return [
            Member(m, guild_id=guild_id, state=self._state)
            for m in await self._state.http.request(
                Path("GET", "guilds/{guild_id}/members/search", guild_id=guild_id),
                params=assign_val_dict({"query": query}, _MISSING, limit=limit),
            )
        ]

    async def modify_member(
        self,
        guild_id: int,
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
        return Member(
            await self._state.http.request(
                Path(
                    "PATCH",
                    "guilds/{guild_id}/members/{user_id}",
                    guild_id=guild_id,
                    user_id=user_id,
                ),
                json=assign_val_dict(
                    {},
                    _MISSING,
                    nick=nick,
                    roles=roles,
                    mute=mute,
                    deaf=deaf,
                    channel_id=channel_id,
                    communication_disabled_until=(
                        communication_disabled_until.isoformat()
                        if isinstance(communication_disabled_until, datetime)
                        else communication_disabled_until
                    ),
                ),
                audit_log_reason=audit_log_reason,
            ),
            guild_id=guild_id,
            user_id=user_id,
            state=self._state,
        )

    async def modify_self_member(
        self,
        guild_id: int,
        *,
        nick: str | None = _MISSING,
        banner: File | str | None = _MISSING,
        avatar: File | str | None = _MISSING,
        bio: str | None = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> Member:
        return Member(
            await self._state.http.request(
                Path("PATCH", "/guilds/{guild_id}/members/@me", guild_id=guild_id),
                json=assign_val_dict(
                    {},
                    _MISSING,
                    nick=nick,
                    banner=await maybe_encode_file(banner),
                    avatar=await maybe_encode_file(avatar),
                    bio=bio,
                ),
                audit_log_reason=audit_log_reason,
            ),
            guild_id=guild_id,
            state=self._state,
        )

    async def add_member_role(
        self,
        guild_id: int,
        user_id: int,
        role_id: int,
        *,
        audit_log_reason: str = _MISSING,
    ) -> Member:
        return Member(
            await self._state.http.request(
                Path(
                    "PUT",
                    "guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                    guild_id=guild_id,
                    user_id=user_id,
                    role_id=role_id,
                ),
                audit_log_reason=audit_log_reason,
            ),
            guild_id=guild_id,
            user_id=user_id,
            state=self._state,
        )

    async def remove_member_role(
        self,
        guild_id: int,
        user_id: int,
        role_id: int,
        *,
        audit_log_reason: str = _MISSING,
    ) -> None:
        await self._state.http.request(
            Path(
                "DELETE",
                "guilds/{guild_id}/members/{user_id}/roles/{role_id}",
                guild_id=guild_id,
                user_id=user_id,
                role_id=role_id,
            ),
            audit_log_reason=audit_log_reason,
        )

    async def remove_member(
        self, guild_id: int, user_id: int, *, audit_log_reason: str = _MISSING
    ) -> None:
        await self._state.http.request(
            Path(
                "DELETE",
                "guilds/{guild_id}/members/{user_id}",
                guild_id=guild_id,
                user_id=user_id,
            ),
            audit_log_reason=audit_log_reason,
        )

    @overload
    async def fetch_bans(
        self,
        guild_id: int,
        *,
        limit: int = _MISSING,
        before: int,
    ) -> list[GuildBan]: ...

    @overload
    async def fetch_bans(
        self, guild_id: int, *, limit: int = _MISSING, after: int
    ) -> list[GuildBan]: ...

    @overload
    async def fetch_bans(
        self,
        guild_id: int,
        *,
        limit: int = _MISSING,
    ) -> list[GuildBan]: ...

    async def fetch_bans(
        self,
        guild_id: int,
        *,
        limit: int = _MISSING,
        before: int = _MISSING,
        after: int = _MISSING,
    ) -> list[GuildBan]:
        return [
            GuildBan(b, state=self._state)
            for b in await self._state.http.request(
                Path("GET", "guilds/{guild_id}/bans", guild_id=guild_id),
                params=assign_val_dict(
                    {}, _MISSING, limit=limit, before=before, after=after
                ),
            )
        ]

    async def fetch_ban(self, guild_id: int, user_id: int) -> GuildBan:
        return GuildBan(
            await self._state.http.request(
                Path(
                    "GET",
                    "guilds/{guild_id}/bans/{user_id}",
                    guild_id=guild_id,
                    user_id=user_id,
                )
            ),
            state=self._state,
        )

    async def create_ban(
        self,
        guild_id: int,
        user_id: int,
        *,
        delete_message: timedelta | int = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> None:
        await self._state.http.request(
            Path(
                "PUT",
                "guilds/{guild_id}/bans/{user_id}",
                guild_id=guild_id,
                user_id=user_id,
            ),
            json=assign_val_dict(
                {}, _MISSING, delete_message_seconds=mgetattr(delete_message, "seconds")
            ),
            audit_log_reason=audit_log_reason,
        )

    async def remove_ban(
        self, guild_id: int, user_id: int, *, audit_log_reason: str = _MISSING
    ) -> None:
        await self._state.http.request(
            Path(
                "DELETE",
                "guilds/{guild_id}/bans/{user_id}",
                guild_id=guild_id,
                user_id=user_id,
            ),
            audit_log_reason=audit_log_reason,
        )

    async def bulk_ban(
        self,
        guild_id: int,
        user_ids: list[int],
        *,
        delete_message_seconds: int = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> BulkBanResult:
        return BulkBanResult._from_dict(
            await self._state.http.request(
                Path("POST", "guilds/{guild_id}/bulk-ban", guild_id=guild_id),
                json=assign_val_dict(
                    {"user_ids": user_ids},
                    _MISSING,
                    delete_message_seconds=delete_message_seconds,
                ),
                audit_log_reason=audit_log_reason,
            )
        )

    async def fetch_roles(self, guild_id: int) -> list[Role]:
        return [
            Role(r)
            for r in await self._state.http.request(
                Path("GET", "guilds/{guild_id}/roles", guild_id=guild_id),
            )
        ]

    async def fetch_role(self, guild_id: int, role_id: int) -> Role:
        return Role(
            await self._state.http.request(
                Path(
                    "GET",
                    "guilds/{guild_id}/roles/{role_id}",
                    guild_id=guild_id,
                    role_id=role_id,
                ),
            )
        )

    async def fetch_role_member_counts(self, guild_id: int) -> dict[int, int]:
        return {
            int(k): v
            for k, v in (
                cast(
                    dict[str, int],
                    await self._state.http.request(
                        Path(
                            "GET",
                            "guilds/{guild_id}/roles/member-counts",
                            guild_id=guild_id,
                        )
                    ),
                )
            ).items()
        }

    async def create_role(
        self,
        guild_id: int,
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
        return Role(
            await self._state.http.request(
                Path("POST", "guilds/{guild_id}/roles", guild_id=guild_id),
                json=assign_val_dict(
                    {},
                    _MISSING,
                    name=name,
                    permissions=mgetattr(permissions, "value"),
                    colors=mtd(colors),
                    hoist=hoist,
                    icon=await maybe_encode_file(icon),
                    unicode_emoji=unicode_emoji,
                    mentionable=mentionable,
                ),
                audit_log_reason=audit_log_reason,
            )
        )

    async def edit_role_positions(
        self,
        guild_id: int,
        *changes: RolePositionChange,
        audit_log_reason: str = _MISSING,
    ) -> list[Role]:
        return [
            Role(d)
            for d in cast(
                list[RolePayload],
                await self._state.http.request(
                    Path("PATCH", "guilds/{guild_id}/roles", guild_id=guild_id),
                    json=maybe_iter(changes),
                    audit_log_reason=audit_log_reason,
                ),
            )
        ]

    async def edit_role(
        self,
        guild_id: int,
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
        return Role(
            cast(
                RolePayload,
                await self._state.http.request(
                    Path(
                        "PATCH",
                        "guilds/{guild_id}/roles/{role_id}",
                        guild_id=guild_id,
                        role_id=role_id,
                    ),
                    json=assign_val_dict(
                        {},
                        _MISSING,
                        name=name,
                        permissions=mgetattr(permissions, "value"),
                        colors=mtd(colors),
                        hoist=hoist,
                        icon=await maybe_encode_file(icon),
                        unicode_emoji=unicode_emoji,
                        mentionable=mentionable,
                    ),
                    audit_log_reason=audit_log_reason,
                ),
            )
        )

    async def delete_role(
        self, guild_id: int, role_id: int, *, audit_log_reason: str = _MISSING
    ) -> None:
        await self._state.http.request(
            Path(
                "DELETE",
                "guilds/{guild_id}/roles/{role_id}",
                guild_id=guild_id,
                role_id=role_id,
            ),
            audit_log_reason=audit_log_reason,
        )

    async def fetch_guild_prune_count(
        self,
        guild_id: int,
        *,
        days: int = _MISSING,
        include_roles: list[int] = _MISSING,
    ) -> int:
        return (
            cast(
                dict[str, int],
                await self._state.http.request(
                    Path("GET", "guilds/{guild_id}/prune", guild_id=guild_id),
                    params=assign_val_dict(
                        {},
                        _MISSING,
                        days=days,
                        include_roles=(
                            ",".join([str(x) for x in include_roles])
                            if include_roles is not _MISSING
                            else _MISSING
                        ),
                    ),
                ),
            )
        )["pruned"]

    @overload
    async def start_prune(
        self,
        guild_id: int,
        *,
        days: int = _MISSING,
        compute_prune_count: Literal[True] = _MISSING,
        include_roles: list[int] = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> int: ...

    @overload
    async def start_prune(
        self,
        guild_id: int,
        *,
        days: int = _MISSING,
        compute_prune_count: Literal[False],
        include_roles: list[int] = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> None: ...

    async def start_prune(
        self,
        guild_id: int,
        *,
        days: int = _MISSING,
        compute_prune_count: bool = _MISSING,
        include_roles: list[int] = _MISSING,
        audit_log_reason: str = _MISSING,
    ) -> int | None:
        return (
            cast(
                dict[str, int | None],
                await self._state.http.request(
                    Path("POST", "guilds/{guild_id}/prune", guild_id=guild_id),
                    json=assign_val_dict(
                        {},
                        _MISSING,
                        days=days,
                        compute_prune_count=compute_prune_count,
                        include_role=include_roles,
                    ),
                    audit_log_reason=audit_log_reason,
                ),
            )
        )["pruned"]
