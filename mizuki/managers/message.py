from typing import overload

from ..enums.message import MessageReferenceType
from ..flags import MessageFlags
from ._types import BaseManager
from ..http import Path
from ..objects.message import AllowedMentions, Message, MessageReference
from ..objects.embed import Embed

from .._utils import _MISSING, assign_val_dict, mtd

__all__ = (
    "MessageManager",
)

class MessageManager(BaseManager):
    """"
    Manager used to fetch :class:`Message <mizuki.objects.message.Message>` objects.
    """

    __slots__ = ()

    def get(self, message_id: int) -> Message | None:
        """
        Attempts to fetch a :class:`Message <mizuki.objects.message.Message>` from the internal cache of the bot.
        
        Parameters
        ----------
        message_id: :class:`int`
            The message_id of the message to fetch.
            
        Returns
        -------
        :class:`Message <mizuki.objects.message.Message>`
            The Messsge received from the cache.
        :class:`None`
            Could not find the User object in the internal cache.
        """
        return self._cache_storage.get_message(message_id)

    async def fetch(self, channel_id: int, message_id: int) -> Message:
        """
        Attempts to fetch a :class:`Message <mizuki.objects.message.Message>` from the Discord API.
        
        Parameters
        ----------
        message_id: :class:`int`
            The message_id of the message to fetch.
          
        Raises
        ------
        :class:`NotFound`
            Could not find an message with that ID.

        :class:`Forbidden`
            You are not allowed to fetch that message.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_messages(
            Message(await self._http.request(
                Path(
                    "GET",
                    "channels/{channel_id}/messages/{message_id}",
                    channel_id=channel_id,
                    message_id=message_id
                )
            ))
        )

    async def get_or_fetch(self, channel_id: int, message_id: int) -> Message:
        """
        A couroutine function that attempts to fetch a :class:`Message <mizuki.objects.message.Message>` from internal cache and if not present, makes an API call to discord.
        
        Parameters
        ----------
        message_id: :class:`int`
            The message_id of the message to fetch.
            
        Raises
        ------
        :class:`NotFound`
            Could not find an message with that ID.

        :class:`Forbidden`
            You are not allowed to fetch that message.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return self.get(message_id) or await self.fetch(channel_id, message_id)

    @overload
    async def fetch_channel_messages(
        self, channel_id: int,
        *,
        around: int = _MISSING,
        limit: int = _MISSING
    ) -> list[Message]: ...

    @overload
    async def fetch_channel_messages(
        self, channel_id: int,
        *,
        before: int = _MISSING,
        limit: int = _MISSING
    ) -> list[Message]: ...

    @overload
    async def fetch_channel_messages(
        self, channel_id: int,
        *,
        after: int = _MISSING,
        limit: int = _MISSING
    ) -> list[Message]: ...

    async def fetch_channel_messages(
        self, channel_id: int,
        *,
        around: int = _MISSING,
        before: int = _MISSING,
        after: int = _MISSING,
        limit: int = _MISSING
    ) -> list[Message]:
        """
        Fetches the message in a channel based on the parameters.
        
        On a Guild Channel, :attr:`VIEW_CHANNEL <mizuki.objects.permissions.Permissions.VIEW_CHANNEL>` (as well as :attr:`CONNECT <mizuki.objects.permissions.Permissions.CONNECT>` for a voice channel) are needed for fetching messages.

        Returns an empty array if missing :attr:`READ_MESSAGE_HISTORY <mizuki.objects.permissions.Permissions.READ_MESSAGE_HISTORY>`.

        .. note::

            The before, after, and around parameters are mutually exclusive, only one may be passed at a time.

        Parameters
        ----------
        channel_id : :class:`int`
            The channel ID to fetch messages from.

        around : :class:`int`, optional
            To fetch messages around this message ID.

        before : :class:`int`, optional
            To fetch messages before this message ID.
        
        after : :class:`int`, optional
            To fetch messages after this message ID.
        
        limit : :class:`int`, optional
            Max number of messages to return. Can be 1-100. By default, Discord will set the limit to 50 messages.

        Raises
        ------
        :class:`NotFound`
            Could not find an message with that ID.

        :class:`Forbidden`
            You are not allowed to fetch those messages.

        :class:`HTTPException`
            A HTTP error occured.
        """
        params = assign_val_dict(
            {}, _MISSING,
            around=around,
            before=before,
            after=after
        )

        if len(params) > 1: raise TypeError("'around', 'before', and 'after' parameters are mutually exclusive. Only one should be provided at a time.")

        return [
            self._cache_storage.update_messages(Message(m))
            for m in await self._http.request(
                Path(
                    "GET",
                    "channels/{channel_id}/messages",
                    channel_id=channel_id
                ),
                params=assign_val_dict(params, _MISSING, limit=limit)
            )
        ]

    async def create(
        self, channel_id: int,
        *,
        content: str = _MISSING,
        tts: bool = _MISSING,
        embeds: list[Embed] = _MISSING,
        allowed_mentions: AllowedMentions = _MISSING,
        message_reference: MessageReference = _MISSING,
        sticker_ids: list[int] = _MISSING,
        flags: MessageFlags = _MISSING
    ) -> Message:
        """
        Creates a new message in the specified channel.
        
        .. note::
            
            At least one of, ``content``, ``embeds``, ``sticker_ids`` is required. For forwarding, only ``message_reference`` is required.
        
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
            
        allowed_mentions : :class:`AllowedMentions <mizuki.objects.message.AllowedMentions>`
            The AllowedMentions object that dictates whether user, role or everyone pings are enabled.
            
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
            A HTTP error occured.
        """
        return self._cache_storage.update_messages(
            Message(await self._http.request(
                Path(
                    "POST",
                    "channels/{channel_id}/messages",
                    channel_id=channel_id
                ),
                json=assign_val_dict(
                    {}, _MISSING,
                    content=content,
                    tts=tts,
                    embeds=(
                        [e._to_dict() for e in embeds]
                        if embeds is not _MISSING else _MISSING
                    ),
                    allowed_mentions=mtd(allowed_mentions),
                    message_reference=mtd(message_reference),
                    sticker_ids=sticker_ids,
                    flags=flags.value if flags is not _MISSING else _MISSING
                )
            ))
        )
        
    async def reply(
        self, 
        channel_id: int,
        message_id: int,
        *,
        content: str = _MISSING,
        tts: bool = _MISSING,
        embeds: list[Embed] = _MISSING,
        allowed_mentions: AllowedMentions = _MISSING,
        sticker_ids: list[int] = _MISSING,
        flags: MessageFlags = _MISSING   
    ) -> Message:
        """
        Creates a new reply to a message in the specified channel.
        
        .. note::
            
            At least one of, ``content``, ``embeds``, ``sticker_ids`` is required.
        
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
            
        allowed_mentions : :class:`AllowedMentions <mizuki.objects.message.AllowedMentions>`
            The AllowedMentions object that dictates whether user, role or everyone pings are enabled.
            
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
            A HTTP error occured.
        """
        return await self.create(
            channel_id,
            content=content,
            tts=tts,
            embeds=embeds,
            allowed_mentions=allowed_mentions,
            message_reference=MessageReference.new(message_id=message_id),
            sticker_ids=sticker_ids,
            flags=flags
        )
    
    async def forward(
        self, target_channel_id: int,
        *,
        message_id: int,
        channel_id: int,
        guild_id: int = _MISSING
    ) -> Message:
        """
        Forwards a message to a channel.
        
        Parameters
        ----------
        target_channel_id : :class:`int`
            The ID of the Channel to forward to.
        
        message_id : :class:`int`
            The ID to the message to forward.
            
        channel_id : :class:`int`
            The ID of the channel to forward from.
            
        guild_id : :class:`int`, optional
            The ID of the Guild to forward from.

        Raises
        ------
        :class:`NotFound`
            The channel you tried to send to doesn't exist or the message you tried to forward doesn't exist.

        :class:`Forbidden`
            You are not allowed to send the message. You may be missing a specific permission.

        :class:`HTTPException`
            A HTTP error occured.
        """
        return await self.create(target_channel_id,
            message_reference=MessageReference.new(
                type=MessageReferenceType.FORWARD,
                message_id=message_id,
                channel_id=channel_id,
                guild_id=guild_id
            )
        )

    async def crosspost(
        self,
        channel_id: int,
        message_id: int
    ) -> Message:
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
            A HTTP error occured.
        """
        return self._cache_storage.update_messages(
            Message(await self._http.request(
                Path(
                    "POST",
                    "channels/{channel_id}/messages/{message_id}/crosspost",
                    message_id=message_id,
                    channel_id=channel_id
                )
            ))
        )