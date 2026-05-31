from .objects.user import User
from .objects.message import Message
from .objects.guild import Guild
from .objects.channel import GuildChannel, PrivateChannel, ThreadChannel, parse_channel_payload
from .http import HTTPClient, Path
from .cache import CacheStorage

class BaseManager:
    ":meta private:"
    __slots__ = (
        "_http",
        "_cache_storage"
    )

    def __init__(self, client: HTTPClient, cache: CacheStorage):
        self._http = client
        self._cache_storage = cache

class UserManager(BaseManager):
    """
    Manager used to fetch :class:`User <dispy.objects.user.User>` objects.

    :meta public:
    """

    __slots__ = ()

    def get(self, user_id: int) -> User | None:
        """
        Attempts to fetch a :class:`User <dispy.objects.user.User>` from the internal cache of the bot.
        
        Parameters
        ----------
        user_id: :class:`int`
            The user_id of the user to fetch.
            
        Returns
        -------
        :class:`User <dispy.objects.user.User>`
            The User received from the cache.
        :class:`None`
            Could not find the User object in the internal cache.
        """
        return self._cache_storage.get_user(user_id)

    async def fetch(self, user_id: int) -> User:
        """
        Attempts to fetch a :class:`User <dispy.objects.user.User>` from the Discord API.
        
        Parameters
        ----------
        user_id: :class:`int`
            The user_id of the user to fetch.
            
        Returns
        -------
        :class:`User <dispy.objects.user.User>`
            The User object recieved from Discord API.
            
        Raises
        ------
        :class:`NotFound`
            Could not find an user with that ID.
        :class:`HTTPException`
            A HTTP error occured.
        """
        return self._cache_storage.update_users(
            User(await self._http.request(
                Path(
                    "GET",
                    "users/{user_id}",
                    user_id=user_id
            )))
        )

    async def get_or_fetch(self, user_id: int) -> User:
        """
        A couroutine function that attempts to fetch a :class:`User <dispy.objects.user.User>` from internal cache and if not present, makes an API call to discord.
        
        Parameters
        ----------
        user_id: :class:`int`
            The user_id of the user to fetch.
            
        Returns
        -------
        :class:`User <dispy.objects.user.User>`
            The User object recieved from Discord API or cache.
            
        Raises
        ------
        :class:`NotFound`
            Could not find an user with that ID.
        :class:`HTTPException`
            A HTTP error occured.
        """
        return self.get(user_id) or await self.fetch(user_id)

class MessageManager(BaseManager):
    """"
    Manager used to fetch :class:`Message <dispy.objects.message.Message>` objects.
    
    :meta public:
    """

    __slots__ = ()

    def get(self, message_id: int) -> Message | None:
        """
        Attempts to fetch a :class:`Message <dispy.objects.message.Message>` from the internal cache of the bot.
        
        Parameters
        ----------
        message_id: :class:`int`
            The message_id of the message to fetch.
            
        Returns
        -------
        :class:`Message <dispy.objects.message.Message>`
            The Messsge received from the cache.
        :class:`None`
            Could not find the User object in the internal cache.
        """
        return self._cache_storage.get_message(message_id)

    async def fetch(self, channel_id: int, message_id: int) -> Message:
        """
        Attempts to fetch a :class:`Message <dispy.objects.message.Message>` from the Discord API.
        
        Parameters
        ----------
        message_id: :class:`int`
            The message_id of the message to fetch.
            
        Returns
        -------
        :class:`Message <dispy.objects.message.Message>`
            The Message object recieved from Discord API.
            
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
            )))
        )

    async def get_or_fetch(self, channel_id: int, message_id: int) -> Message:
        """
        A couroutine function that attempts to fetch a :class:`Message <dispy.objects.message.Message>` from internal cache and if not present, makes an API call to discord.
        
        Parameters
        ----------
        message_id: :class:`int`
            The message_id of the message to fetch.
            
        Returns
        -------
        :class:`Message <dispy.objects.message.Message>`
            The Message object recieved from Discord API or cache.
            
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

class ChannelManager(BaseManager):
    """
    Manager used to fetch :class:`PrivateChannel <dispy.objects.channel.PrivateChannel>`, :class:`GuildChannel <dispy.objects.channel.GuildChannel>` or :class:`ThreadChannel <dispy.objects.channel.ThreadChannel>` objects.
    
    :meta public:
    """
    
    __slots__ = ()

    def get(self, channel_id: int) -> ThreadChannel | GuildChannel | PrivateChannel | None:
        """
        Attempts to fetch a :class:`PrivateChannel <dispy.objects.channel.PrivateChannel>`, :class:`GuildChannel <dispy.objects.channel.GuildChannel>` or :class:`ThreadChannel <dispy.objects.channel.ThreadChannel>` from the internal cache of the bot.
        
        Parameters
        ----------
        channel_id: :class:`int`
            The channel_id of the channel to fetch.
            
        Returns
        -------
        :class:`PrivateChannel <dispy.objects.channel.PrivateChannel>`
            The PrivateChannel object recieved from the cache.
        :class:`GuildChannel <dispy.objects.channel.GuildChannel>`
            The GuildChannel object recieved from the cache.
        :class:`ThreadChannel <dispy.objects.channel.ThreadChannel>`
            The ThreadChannel object received from the cache.
        :class:`None`
            The Channel could not be found in the cache.
        """
        return self._cache_storage.get_channel(channel_id)

    async def fetch(self, channel_id: int) -> ThreadChannel | GuildChannel | PrivateChannel:
        """
        Attempts to fetch a :class:`PrivateChannel <dispy.objects.channel.PrivateChannel>`, :class:`GuildChannel <dispy.objects.channel.GuildChannel>` or :class:`ThreadChannel <dispy.objects.channel.ThreadChannel>` from the Discord API.
        
        Parameters
        ----------
        channel_id: :class:`int`
            The channel_id of the channel to fetch.
            
        Returns
        -------
        :class:`PrivateChannel <dispy.objects.channel.PrivateChannel>`
            The PrivateChannel object recieved from Discord API.
        :class:`GuildChannel <dispy.objects.channel.GuildChannel>`
            The GuildChannel object recieved from the Discord API.
        :class:`ThreadChannel <dispy.objects.channel.ThreadChannel>`
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
        A couroutine function that attempts to fetch a :class:`PrivateChannel <dispy.objects.channel.PrivateChannel>`, :class:`GuildChannel <dispy.objects.channel.GuildChannel>` or :class:`ThreadChannel <dispy.objects.channel.ThreadChannel>` from internal cache and if not present, makes an API call to discord.
        
        Parameters
        ----------
        channel_id: :class:`int`
            The channel_id of the channel to fetch.
            
        Returns
        -------
        :class:`PrivateChannel <dispy.objects.channel.PrivateChannel>`
            The PrivateChannel object recieved from Discord API.
        :class:`GuildChannel <dispy.objects.channel.GuildChannel>`
            The GuildChannel object recieved from the Discord API.
        :class:`ThreadChannel <dispy.objects.channel.ThreadChannel>`
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


class GuildManager(BaseManager):
    """
    Manager used to fetch :class:`Guild <dispy.objects.guild.Guild>` objects.
    
    :meta public:
    """

    __slots__ = ()

    def get(self, guild_id: int) -> Guild | None:
        """
        Attempts to fetch a :class:`Guild <dispy.objects.guild.Guild>` from the internal cache of the bot.
        
        Parameters
        ----------
        guild_id: :class:`int`
            The guild_id of the guild to fetch.
            
        Returns
        -------
        :class:`Guild <dispy.objects.guild.Guild>`
            The Guild received from the cache.
        :class:`None`
            Could not find the Guild object in the internal cache.
        """
        return self._cache_storage.get_guild(guild_id)

    async def fetch(self, guild_id: int) -> Guild:
        """
        Attempts to fetch a :class:`Guild <dispy.objects.guild.Guild>` from the Discord API.
        
        Parameters
        ----------
        guild_id: :class:`int`
            The guild_id of the guild to fetch.
            
        Returns
        -------
        :class:`Guild <dispy.objects.guild.Guild>`
            The Message object recieved from Discord API.
            
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
            Guild(await self._http.request(
                Path(
                    "GET",
                    "guilds/{guild_id}",
                    guild_id=guild_id
            )))
        )
    
    async def get_or_fetch(self, guild_id: int) -> Guild:
        """
        A couroutine function that attempts to fetch a :class:`Guild <dispy.objects.guild.Guild>` from internal cache and if not present, makes an API call to discord.

        Parameters
        ----------
        guild_id: :class:`int`
            The guild_id of the guild to fetch.
            
        Returns
        -------
        :class:`Guild <dispy.objects.guild.Guild>`
            The Message object recieved from Discord API.
            
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