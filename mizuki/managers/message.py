from typing import Any, overload, TYPE_CHECKING

from mizuki.http import Path
from mizuki.file import File
from mizuki.flags import MessageFlags
from mizuki._utils import _MISSING, assign_val_dict, maybe_iter, mtd

from mizuki.managers._types import BaseManager
from mizuki.enums.message import MessageReferenceType, ReactionType
from mizuki.objects.embed import Embed
from mizuki.objects.user import User
from mizuki.objects.message import AllowedMentions, Message, MessageReference

if TYPE_CHECKING:
    from mizuki.objects.components import Component

__all__ = ("MessageManager",)


class MessageManager(BaseManager):
    """
    Manager used to fetch :class:`Message <mizuki.objects.message.Message>` objects.
    """

    __slots__ = ()

    def get(self, message_id: int) -> Message | None:
        """
        Attempts to fetch a :class:`Message <mizuki.objects.message.Message>` from the internal cache of the bot.

        Parameters
        ----------
        message_id: :class:`int`
            The ID of the message to fetch.

        Returns
        -------
        :class:`Message <mizuki.objects.message.Message>`
            The Message received from the cache.
        :class:`None`
            Could not find the Message object in the internal cache.
        """
        return self._cache_storage.get_message(message_id)

    async def fetch(self, channel_id: int, message_id: int) -> Message:
        """
        Attempts to fetch a :class:`Message <mizuki.objects.message.Message>` from the Discord API.

        Parameters
        ----------
        message_id: :class:`int`
            The ID of the message to fetch.

        Raises
        ------
        :class:`NotFound`
            Could not find a message with that ID.

        :class:`Forbidden`
            You are not allowed to fetch that message.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return self._cache_storage.update_messages(
            Message(
                await self._state.http.request(
                    Path(
                        "GET",
                        "channels/{channel_id}/messages/{message_id}",
                        channel_id=channel_id,
                        message_id=message_id,
                    )
                ),
                state=self._state,
            )
        )

    async def get_or_fetch(self, channel_id: int, message_id: int) -> Message:
        """
        A coroutine function that attempts to fetch a :class:`Message <mizuki.objects.message.Message>` from internal cache and if not present, fetches it from Discord.

        Parameters
        ----------
        message_id: :class:`int`
            The message_id of the message to fetch.

        Raises
        ------
        :class:`NotFound`
            Could not find a message with that ID.

        :class:`Forbidden`
            You are not allowed to fetch that message.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return self.get(message_id) or await self.fetch(channel_id, message_id)

    @overload
    async def fetch_channel_messages(
        self, channel_id: int, *, around: int = _MISSING, limit: int = _MISSING
    ) -> list[Message]: ...

    @overload
    async def fetch_channel_messages(
        self, channel_id: int, *, before: int = _MISSING, limit: int = _MISSING
    ) -> list[Message]: ...

    @overload
    async def fetch_channel_messages(
        self, channel_id: int, *, after: int = _MISSING, limit: int = _MISSING
    ) -> list[Message]: ...

    async def fetch_channel_messages(
        self,
        channel_id: int,
        *,
        around: int = _MISSING,
        before: int = _MISSING,
        after: int = _MISSING,
        limit: int = _MISSING,
    ) -> list[Message]:
        """
        Fetches the messages in a channel based on the parameters.

        On a Guild Channel, :attr:`VIEW_CHANNEL <mizuki.objects.permissions.Permissions.VIEW_CHANNEL>` (as well as :attr:`CONNECT <mizuki.objects.permissions.Permissions.CONNECT>` for a voice channel) are needed for fetching messages.

        Returns an empty array if missing :attr:`READ_MESSAGE_HISTORY <mizuki.objects.permissions.Permissions.READ_MESSAGE_HISTORY>`.

        .. note::

            The before, after, and around parameters are mutually exclusive, only one may be passed at a time.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel to fetch messages from.

        around : :class:`int`, optional
            To fetch messages around this message ID.

        before : :class:`int`, optional
            To fetch messages before this message ID.

        after : :class:`int`, optional
            To fetch messages after this message ID.

        limit : :class:`int`, optional
            Max number of messages to return. Can be 1-100. Defaults to 50.

        Raises
        ------
        :class:`NotFound`
            Could not find a message with that ID.

        :class:`Forbidden`
            You are not allowed to fetch those messages.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        params = assign_val_dict(
            {}, _MISSING, around=around, before=before, after=after
        )

        if len(params) > 1:
            raise TypeError(
                "'around', 'before', and 'after' parameters are mutually exclusive. Only one should be provided at a time."
            )

        return [
            self._cache_storage.update_messages(Message(m, state=self._state))
            for m in await self._state.http.request(
                Path("GET", "channels/{channel_id}/messages", channel_id=channel_id),
                params=assign_val_dict(params, _MISSING, limit=limit),
            )
        ]

    async def create(
        self,
        channel_id: int,
        *,
        content: str = _MISSING,
        tts: bool = _MISSING,
        embeds: list[Embed] = _MISSING,
        components: list[Component] = _MISSING,
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
        channel_id : :class:`int`
            The ID of the Channel to send message to.

        content : :class:`str`
            The content of the message.

        tts : :class:`bool`
            Whether TTS is enabled for the message.

        embeds : list[:class:`Embed <mizuki.objects.embed.Embed>`]
            The list of embeds to send along the message.

        components : list[:class:`Component <mizuki.objects.component.Component>`]
            The list of components to send in this message.

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
        return self._cache_storage.update_messages(
            Message(
                await self._state.http.request(
                    Path(
                        "POST", "channels/{channel_id}/messages", channel_id=channel_id
                    ),
                    files=files,
                    components=components,
                    json=assign_val_dict(
                        {},
                        _MISSING,
                        content=content,
                        tts=tts,
                        embeds=maybe_iter(embeds),
                        components=maybe_iter(components),
                        attachments=(
                            maybe_iter(
                                files,
                                enumerate_iter=True,
                                method=lambda i, a: a._to_attachment_dict(i),
                            )
                            if MessageFlags.IS_COMPONENTS_V2
                            not in (flags or MessageFlags(0))
                            else _MISSING
                        ),
                        allowed_mentions=mtd(allowed_mentions),
                        message_reference=mtd(message_reference),
                        sticker_ids=sticker_ids,
                        flags=flags.value if flags is not _MISSING else _MISSING,
                    ),
                ),
                state=self._state,
            )
        )

    async def reply(
        self,
        channel_id: int,
        message_id: int,
        *,
        content: str = _MISSING,
        tts: bool = _MISSING,
        embeds: list[Embed] = _MISSING,
        components: list[Component] = _MISSING,
        allowed_mentions: AllowedMentions = _MISSING,
        files: list[File] = _MISSING,
        sticker_ids: list[int] = _MISSING,
        flags: MessageFlags = _MISSING,
    ) -> Message:
        """
        Creates a new reply to a message in the specified channel.

        .. note::

            At least one of, ``content``, ``embeds``, ``sticker_ids``, ``files`` must be provided.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the Channel to send reply to.

        message_id : :class:`int`
            The ID of the Message to reply to.

        content : :class:`str`
            The content of the message.

        tts : :class:`bool`
            Whether TTS is enabled for the message.

        embeds : list[:class:`Embed <mizuki.objects.embed.Embed>`]
            The list of embeds to send along the message.

        components : list[:class:`Component <mizuki.objects.component.Component>`]
            The list of components to send in this message.

        allowed_mentions : :class:`AllowedMentions <mizuki.objects.message.AllowedMentions>`
            The AllowedMentions object that dictates whether user, role or everyone pings are enabled.

        files : list[:class:`File <mizuki.file.File>`]
            The files to upload with the message.

        sticker_ids : list[:class:`int`]
            The Guild Stickers to send with the message. Max 3.

        flags : :class:`MessageFlags <mizuki.flags.MessageFlags>`
            The MessageFlags of the new message.

        Raises
        ------
        :class:`NotFound`
            The channel you tried to send to doesn't exist or the message you replied to doesn't exist.

        :class:`Forbidden`
            You are not allowed to send the message. You may be missing a specific permission.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return await self.create(
            channel_id,
            content=content,
            tts=tts,
            embeds=embeds,
            components=components,
            allowed_mentions=allowed_mentions,
            files=files,
            message_reference=MessageReference.new(message_id=message_id),
            sticker_ids=sticker_ids,
            flags=flags,
        )

    async def forward(
        self,
        target_channel_id: int,
        *,
        message_id: int,
        channel_id: int,
        guild_id: int = _MISSING,
    ) -> Message:
        """
        Forwards a message to a channel.

        Parameters
        ----------
        target_channel_id : :class:`int`
            The ID of the target Channel.

        message_id : :class:`int`
            The ID to the message to forward.

        channel_id : :class:`int`
            The ID of the source Channel.

        guild_id : :class:`int`, optional
            The ID of the source Guild.

        Raises
        ------
        :class:`NotFound`
            The channel you tried to send to doesn't exist or the message you tried to forward doesn't exist.

        :class:`Forbidden`
            You are not allowed to send the message. You may be missing a specific permission.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return await self.create(
            target_channel_id,
            message_reference=MessageReference.new(
                type=MessageReferenceType.FORWARD,
                message_id=message_id,
                channel_id=channel_id,
                guild_id=guild_id,
            ),
        )

    async def crosspost(self, channel_id: int, message_id: int) -> Message:
        """
        Crossposts a message from an Announcement Channel to all following channels.

        This requires :attr:`SEND_MESSAGES <mizuki.objects.permissions.Permissions.SEND_MESSAGES>` for your own messages, and
        :attr:`MANAGE_MESSAGES <mizuki.objects.permissions.Permissions.MANAGE_MESSAGES>` when crossposting messages sent by others.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the announcement channel.

        message_id : :class:`int`
            The ID of the message to crosspost.

        Raises
        ------
        :class:`NotFound`
            The channel you tried to crosspost from doesn't exist or the message you tried to crosspost doesn't exist.

        :class:`Forbidden`
            You are not allowed to crosspost the message. You may be missing a specific permission.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return self._cache_storage.update_messages(
            Message(
                await self._state.http.request(
                    Path(
                        "POST",
                        "channels/{channel_id}/messages/{message_id}/crosspost",
                        message_id=message_id,
                        channel_id=channel_id,
                    )
                ),
                state=self._state,
            )
        )

    async def _react_endpoints(
        self,
        method: str,
        *,
        channel_id: int,
        message_id: int,
        emoji_id: int = _MISSING,
        emoji_name: str = _MISSING,
        user: int | str = _MISSING,
        **params: Any,
    ) -> Any:
        suffix = ""

        if emoji_name is not _MISSING:
            suffix = (
                f"/{emoji_name}:{emoji_id}"
                if emoji_id is not _MISSING
                else f"/{emoji_name}"
            )

        if user is not _MISSING:
            suffix += f"/{user}"

        return await self._state.http.request(
            Path(
                method,
                "channels/{channel_id}/messages/{message_id}/reactions{suffix}",
                channel_id=channel_id,
                message_id=message_id,
                suffix=suffix,
                params=params,
            )
        )

    async def react(
        self,
        *,
        channel_id: int,
        message_id: int,
        emoji_id: int = _MISSING,
        emoji_name: str,
    ) -> None:
        """
        Adds a reaction to a message.

        Requires :attr:`READ_MESSAGE_HISTORY <mizuki.objects.permissions.Permissions.READ_MESSAGE_HISTORY>`. Also requires :attr:`ADD_REACTIONS <mizuki.objects.permissions.Permissions.ADD_REACTIONS>` if no one has reacted with this emoji.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel the target message is in.

        message_id : :class:`int`
            The ID of the target message.

        emoji_id : :class:`int`, optional
            The ID of the custom emoji. Omit when reacting with a unicode emoji.

        emoji_name : :class:`str`
            The unicode emoji or the name of the custom emoji.

        Raises
        ------
        :class:`NotFound`
            The message you tried to react to or the emoji you tried to react with wasn't found.

        :class:`Forbidden`
            You are not allowed to react/see the message. You may be missing a specific permission.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        await self._react_endpoints(
            "PUT",
            channel_id=channel_id,
            message_id=message_id,
            emoji_id=emoji_id,
            emoji_name=emoji_name,
            user="@me",
        )

    async def remove_reaction(
        self,
        *,
        channel_id: int,
        message_id: int,
        user_id: int = _MISSING,
        emoji_id: int = _MISSING,
        emoji_name: str,
    ) -> None:
        """
        Removes your reaction from a message.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel the target message is in.

        message_id : :class:`int`
            The ID of the target message.

        user_id : :class:`int`, optional
            The ID of the target user. Defaults to the client user.

        emoji_id : :class:`int`, optional
            The ID of the custom emoji. Omit when reacting with a unicode emoji.

        emoji_name : :class:`str`
            The unicode emoji or the name of the custom emoji.

        Raises
        ------
        :class:`NotFound`
            The message you tried to remove reaction from or the emoji you tried to remove reaction of wasn't found.

        :class:`Forbidden`
            You are not allowed to remove reaction/see the message. You may be missing a specific permission.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        await self._react_endpoints(
            "DELETE",
            channel_id=channel_id,
            message_id=message_id,
            emoji_id=emoji_id,
            emoji_name=emoji_name,
            user=user_id or "@me",
        )

    async def fetch_reactions(
        self,
        *,
        channel_id: int,
        message_id: int,
        emoji_id: int = _MISSING,
        emoji_name: str,
        type: ReactionType = _MISSING,
        after: int = _MISSING,
        limit: int = _MISSING,
    ) -> list[User]:
        """
        Fetch a list of users that reacted with this emoji.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel containing the target message.

        message_id : :class:`int`
            The ID of the target message.

        emoji_id : :class:`int`, optional
            The ID of the custom emoji. Omit when reacting with a unicode emoji.

        emoji_name : :class:`str`
            The unicode emoji or the name of the custom emoji.

        type : :class:`ReactionType <mizuki.enums.message.ReactionType>`, optional
            The type of the reaction to fetch. Defaults to fetches :attr:`NORMAL <mizuki.enums.message.ReactionType.NORMAL>`.

        after : :class:`int`, optional
            To fetch the list starting after the specified user ID.

        limit : :class:`int`, optional
            The max number of users to retrieve. Can be 1-100. Defaults to 25.

        Raises
        ------
        :class:`NotFound`
            The message you tried to fetch reactions of could not be found.

        :class:`Forbidden`
            You are not allowed to fetch the message.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return [
            self._cache_storage.update_users(User(u, state=self._state))
            for u in await self._react_endpoints(
                "GET",
                channel_id=channel_id,
                message_id=message_id,
                emoji_id=emoji_id,
                emoji_name=emoji_name,
                type=(type.value if type is not _MISSING else _MISSING),
                after=after,
                limit=limit,
            )
        ]

    async def delete_emoji_reactions(
        self,
        *,
        channel_id: int,
        message_id: int,
        emoji_id: int = _MISSING,
        emoji_name: str,
    ) -> None:
        """
        Removes all reactions of a specified emoji from a message. This method requires :attr:`MANAGE_MESSAGES <mizuki.objects.permissions.Permissions.MANAGE_MESSAGES>`.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel containing the target message.

        message_id : :class:`int`
            The ID of the target message.

        emoji_id : :class:`int`, optional
            The ID of the custom emoji. Omit when reacting with a unicode emoji.

        emoji_name : :class:`str`
            The unicode emoji or the name of the custom emoji.

        Raises
        ------
        :class:`NotFound`
            The message you tried to do this action on or the emoji does not exist.

        :class:`Forbidden`
            You are not allowed to fetch the message. Or you are missing the permissions to do this action.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        await self._react_endpoints(
            "DELETE",
            channel_id=channel_id,
            message_id=message_id,
            emoji_id=emoji_id,
            emoji_name=emoji_name,
        )

    async def remove_all_reactions(self, *, channel_id: int, message_id: int) -> None:
        """
        Removes all reactions from a message. This method requires :attr:`MANAGE_MESSAGES <mizuki.objects.permissions.Permissions.MANAGE_MESSAGES>`.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel containing the target message.

        message_id : :class:`int`
            The ID of the target message.

        Raises
        ------
        :class:`NotFound`
            The message you tried to do this action on does not exist.

        :class:`Forbidden`
            You are not allowed to fetch the message. Or you are missing the permissions to do this action.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        await self._react_endpoints(
            "DELETE", channel_id=channel_id, message_id=message_id
        )

    async def edit(
        self,
        *,
        channel_id: int,
        message_id: int,
        content: str | None = _MISSING,
        embeds: list[Embed] = _MISSING,
        components: list[Component] = _MISSING,
        flags: MessageFlags = _MISSING,
        allowed_mentions: AllowedMentions | None = _MISSING,
        files: list[File] = _MISSING,
        override_files: bool = True,
    ) -> Message:
        """
        Edits a message sent by you.

        Parameters
        ----------
        channel_id : :class:`int` | :class:`None`
            The ID of the channel the target message is in. Pass ``None`` to clear content.

        message_id : :class:`int`
            The ID of the target message.

        content : :class:`str`
            The content of the message.

        embeds : list[:class:`Embed <mizuki.objects.embed.Embed>`]
            The embeds of the message.

        components : list[:class:`Component <mizuki.objects.component.Component>`]
            The list of components.

        flags : :class:`MessageFlags <mizuki.flags.MessageFlags>`
            The flags of the message.

        allowed_mentions : :class:`AllowedMentions <mizuki.objects.message.AllowedMentions>` | :class:`None`
            The AllowedMentions object that dictates whether user, role or everyone pings are enabled. Pass ``None`` to set this back to default.

        files : list[:class:`File <mizuki.file.File>`]
            The files to upload to the message.

        override_files : :class:`bool`
            Whether to override or append the files to the message. Description is ignored when this is set to ``False``

        Raises
        ------
        :class:`NotFound`
            The message you tried to edit was not found.

        :class:`Forbidden`
            You are not allowed to edit that message.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        return self._cache_storage.update_messages(
            Message(
                await self._state.http.request(
                    Path(
                        "PATCH",
                        "channels/{channel_id}/messages/{message_id}",
                        channel_id=channel_id,
                        message_id=message_id,
                    ),
                    files=files,
                    components=components,
                    json=assign_val_dict(
                        {},
                        _MISSING,
                        content=content,
                        embeds=maybe_iter(embeds),
                        components=maybe_iter(components),
                        flags=(flags.value if flags is not _MISSING else _MISSING),
                        allowed_mentions=mtd(allowed_mentions),
                        attachments=(
                            maybe_iter(
                                files,
                                enumerate_iter=True,
                                method=lambda i, a: a._to_attachment_dict(i),
                            )
                            if override_files
                            else _MISSING
                        ),
                    ),
                ),
                state=self._state,
            )
        )

    async def delete(self, *, channel_id: int, message_id: int) -> None:
        """
        Deletes a message from a channel.

        This method requires :attr:`MANAGE_MESSAGES <mizuki.objects.permissions.Permissions.MANAGE_MESSAGES>` if deleting a message from someone else.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel to delete the message from.

        message_id : :class:`int`
            The ID of the message to delete.

        Raises
        ------
        :class:`NotFound`
            The message you tried to delete does not exist.

        :class:`Forbidden`
            You are not allowed to delete that message.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        await self._state.http.request(
            Path(
                "DELETE",
                "channels/{channel_id}/messages/{message_id}",
                channel_id=channel_id,
                message_id=message_id,
            )
        )
        self._cache_storage.remove_message(message_id)

    async def bulk_delete(self, *, channel_id: int, message_ids: list[int]) -> None:
        """
        Bulk deletes messages from a channel.

        This method requires :attr:`MANAGE_MESSAGES <mizuki.objects.permissions.Permissions.MANAGE_MESSAGES>`.

        Parameters
        ----------
        channel_id : :class:`int`
            The ID of the channel to delete the message from.

        message_ids : list[:class:`int`]
            The list of ID of the messages to delete. Minimum and maximum length of list required are 2 and 100 respectively.

        Raises
        ------
        :class:`NotFound`
            The channel you tried to bulk delete from does not exist.

        :class:`Forbidden`
            You do not have the required permission to bulk delete.

        :class:`HTTPException`
            A HTTP error occurred.
        """
        await self._state.http.request(
            Path(
                "POST",
                "channels/{channel_id}/messages/bulk-delete",
                channel_id=channel_id,
            ),
            json={"message_ids": message_ids},
        )
