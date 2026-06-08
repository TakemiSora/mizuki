from ._types import BaseManager
from ..http import Path
from ..objects.channel import (
    ThreadChannel,
    PrivateChannel,
    GuildChannel,
    parse_channel_payload
)

__all__ = (
    "ChannelManager",
)

class ChannelManager(BaseManager):
    """
    Manager used to fetch :class:`PrivateChannel <mizuki.objects.channel.PrivateChannel>`, :class:`GuildChannel <mizuki.objects.channel.GuildChannel>` or :class:`ThreadChannel <mizuki.objects.channel.ThreadChannel>` objects.
    """
    
    __slots__ = ()

    def get(self, channel_id: int) -> ThreadChannel | GuildChannel | PrivateChannel | None:
        """
        Attempts to fetch a :class:`PrivateChannel <mizuki.objects.channel.PrivateChannel>`, :class:`GuildChannel <mizuki.objects.channel.GuildChannel>` or :class:`ThreadChannel <mizuki.objects.channel.ThreadChannel>` from the internal cache of the bot.
        
        Parameters
        ----------
        channel_id: :class:`int`
            The channel_id of the channel to fetch.
            
        Returns
        -------
        :class:`PrivateChannel <mizuki.objects.channel.PrivateChannel>`
            The PrivateChannel object recieved from the cache.
        :class:`GuildChannel <mizuki.objects.channel.GuildChannel>`
            The GuildChannel object recieved from the cache.
        :class:`ThreadChannel <mizuki.objects.channel.ThreadChannel>`
            The ThreadChannel object received from the cache.
        :class:`None`
            The Channel could not be found in the cache.
        """
        return self._cache_storage.get_channel(channel_id)

    async def fetch(self, channel_id: int) -> ThreadChannel | GuildChannel | PrivateChannel:
        """
        Attempts to fetch a :class:`PrivateChannel <mizuki.objects.channel.PrivateChannel>`, :class:`GuildChannel <mizuki.objects.channel.GuildChannel>` or :class:`ThreadChannel <mizuki.objects.channel.ThreadChannel>` from the Discord API.
        
        Parameters
        ----------
        channel_id: :class:`int`
            The channel_id of the channel to fetch.
            
        Returns
        -------
        :class:`PrivateChannel <mizuki.objects.channel.PrivateChannel>`
            The PrivateChannel object recieved from Discord API.
        :class:`GuildChannel <mizuki.objects.channel.GuildChannel>`
            The GuildChannel object recieved from the Discord API.
        :class:`ThreadChannel <mizuki.objects.channel.ThreadChannel>`
            The ThreadChannel object received from the Discord API.
            
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
            parse_channel_payload(await self._http.request(
                Path(
                    "GET",
                    "channels/{channel_id}",
                    channel_id=channel_id
            )))
        )

    async def get_or_fetch(self, channel_id: int) -> ThreadChannel | GuildChannel | PrivateChannel:
        """
        A couroutine function that attempts to fetch a :class:`PrivateChannel <mizuki.objects.channel.PrivateChannel>`, :class:`GuildChannel <mizuki.objects.channel.GuildChannel>` or :class:`ThreadChannel <mizuki.objects.channel.ThreadChannel>` from internal cache and if not present, makes an API call to discord.
        
        Parameters
        ----------
        channel_id: :class:`int`
            The channel_id of the channel to fetch.
            
        Returns
        -------
        :class:`PrivateChannel <mizuki.objects.channel.PrivateChannel>`
            The PrivateChannel object recieved from Discord API.
        :class:`GuildChannel <mizuki.objects.channel.GuildChannel>`
            The GuildChannel object recieved from the Discord API.
        :class:`ThreadChannel <mizuki.objects.channel.ThreadChannel>`
            The ThreadChannel object received from the Discord API.
            
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