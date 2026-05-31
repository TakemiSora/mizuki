import asyncio
from .objects.user import User
from .objects.message import Message
from .objects.channel import Channel
from .objects.guild import Guild
from dataclasses import dataclass
from datetime import datetime, timedelta

Cachable = User | Message | Channel | Guild

__all__ = (
    "CacheSettings",
)

@dataclass(slots=True)
class CacheEntry[D: Cachable]:
    created_at: datetime
    data: D

class CacheSettings:
    """
    Cache Settings used to determine how cache is handles by a CacheStorage.
    
    In the max limits of cache entries such as :attr:`CacheSettings.max_users_store`, :class:`None` represents infinite or no limit.

    Parameters
    ----------
    users : :class:`bool`, optional
        Toggle caching of :class:`User <dispy.objects.user.User>` objects. Defaults to ``True``.
    messages : :class:`bool`, optional
        Toggle caching of :class:`Message <dispy.objects.message.Message>` objects. Defaults to ``True``.
    channels : :class:`bool`, optional
        Toggle caching of :class:`PrivateChannel <dispy.objects.channel.PrivateChannel>`, :class:`ThreadChannel <dispy.objects.channel.ThreadChannel>` and :class:`GuildChannel <dispy.objects.channel.GuildChannel>` objects. Defaults to ``True``.
    guilds : :class:`bool`, optional
        Toggle caching of :class:`Guild <dispy.objects.guild.Guild>` objects. Defaults to ``True``.
    cache_invalidation : :class:`bool`, optional
        Toggle if cache should be invalidated based on time. Defaults to ``False``.
    invalidation_time : :class:`timedelta <datetime.timedelta>`, optional
        Determines how long a CacheEntry object can live without being invalidated. Defaults to ``timedelta(days=1)``.
    cleanup_interval : :class:`timedelta <datetime.timedelta>`, optional
        Determines how often the Cache will be cleaned up. Defaults to ``timedelta(hours=6)``.
    max_users_store : :class:`int` | :class:`None`, optional
        Determines the max amount of :class:`User <dispy.objects.user.User>` objects the cache will store. Defaults to ``None``.
    max_messages_store : :class:`int` | :class:`None`, optional
        Determines the max amount of :class:`Message <dispy.objects.message.Message>` objects the cache will store. Defaults to ``2000``.
    max_channels_store : :class:`int` | :class:`None`, optional
        Determines the max amount of :class:`PrivateChannel <dispy.objects.channel.PrivateChannel>`, :class:`ThreadChannel <dispy.objects.channel.ThreadChannel>` and :class:`GuildChannel <dispy.objects.channel.GuildChannel>` objects the cache will store. Defaults to ``None``.
    max_guilds_store : :class:`int` | :class:`None`, optional
        Determines the max amount of :class:`Guild <dispy.objects.guild.Guild>` objects the cache will store. Defaults to ``None``.
    """
    
    users: bool
    "Whether :class:`User <dispy.objects.user.User>` caching is enabled."
    
    messages: bool
    "Whether :class:`Message <dispy.objects.message.Message>` caching is enabled."
    
    channels: bool
    "Whether :class:`PrivateChannel <dispy.objects.channel.PrivateChannel>`, :class:`ThreadChannel <dispy.objects.channel.ThreadChannel>` and :class:`GuildChannel <dispy.objects.channel.GuildChannel>` caching is enabled."
    
    guilds: bool
    "Whether :class:`Guild <dispy.objects.guild.Guild>` caching is enabled."
    
    cache_invalidation: bool
    "Whether time-based cache invalidation is enabled."
    
    invalidation_time: timedelta
    "The amount of time a cach can live, before being invalidated."
    
    cleanup_interval: timedelta
    "The interval at which the cleanup tasks will happen."
    
    max_users_store: int | None
    "The max amount of :class:`User <dispy.objects.user.User>` objects the cache will store."
    
    max_messages_store: int | None
    "The max amount of :class:`Message <dispy.objects.message.Message>` objects the cache will store."
    
    max_channels_store: int | None
    "The max amount of :class:`PrivateChannel <dispy.objects.channel.PrivateChannel>`, :class:`ThreadChannel <dispy.objects.channel.ThreadChannel>` and :class:`GuildChannel <dispy.objects.channel.GuildChannel>` objects the cache will store."
    
    max_guilds_store: int | None
    "The max amount of :class:`Guild <dispy.objects.guild.Guild>` objects the cache will store."
    
    __slots__ = (
        "users",
        "messages",
        "channels",
        "guilds",
        "cache_invalidation",
        "invalidation_time",
        "cleanup_interval",
        "max_users_store",
        "max_messages_store",
        "max_channels_store",
        "max_guilds_store"
    )

    def __init__(
        self,
        users: bool = True,
        messages: bool = True,
        channels: bool = True,
        guilds: bool = True,
        cache_invalidation: bool = False,
        invalidation_time: timedelta = timedelta(days=1),
        cleanup_interval: timedelta = timedelta(hours=6),
        max_users_store: int | None = None,
        max_messages_store: int | None = 2000,
        max_channels_store: int | None = None,
        max_guilds_store: int | None = None
    ):
        self.users = users
        self.messages = messages
        self.channels = channels
        self.guilds = guilds
        self.cache_invalidation = cache_invalidation
        self.invalidation_time = invalidation_time
        self.cleanup_interval = cleanup_interval
        self.max_users_store = max_users_store
        self.max_messages_store = max_messages_store
        self.max_channels_store = max_channels_store
        self.max_guilds_store = max_guilds_store

class CacheStorage:
    ":meta private:"
    
    __slots__ = (
        "settings",
        "users",
        "messages",
        "channels",
        "guilds",
        "_users_cleanup_task",
        "_messages_cleanup_task",
        "_channels_cleanup_task",
        "_guilds_cleanup_task"
    )

    def __init__(self, settings: CacheSettings):
        self.settings = settings
        self.users: dict[int, CacheEntry[User]] = {}
        self.messages: dict[int, CacheEntry[Message]] = {}
        self.channels: dict[int, CacheEntry[Channel]] = {}
        self.guilds: dict[int, CacheEntry[Guild]] = {}

    def start_cleanup_tasks(self) -> None:
        self._users_cleanup_task = asyncio.create_task(self._cleanup_cache(self.users))
        self._messages_cleanup_task = asyncio.create_task(self._cleanup_cache(self.messages))
        self._channels_cleanup_task = asyncio.create_task(self._cleanup_cache(self.channels))
        self._guilds_cleanup_task = asyncio.create_task(self._cleanup_cache(self.guilds))

    def _add_to_cache[T: Cachable](self, setting: bool, max_take: int | None, cache: dict[int, CacheEntry[T]], data: T) -> T:
        if setting:
            if max_take is not None and len(cache) > max_take:
                cache.pop(next(iter(cache)))
            if data.id in cache:
                cache.pop(data.id)
            cache[data.id] = CacheEntry[T](datetime.now(), data)
        return data

    def update_users(self, user: User) -> User:
        return self._add_to_cache(
            self.settings.users,
            self.settings.max_users_store,
            self.users, user
        )

    def update_messages(self, message: Message) -> Message:
        return self._add_to_cache(
            self.settings.messages,
            self.settings.max_messages_store,
            self.messages, message
        )

    def update_channels(self, channel: Channel) -> Channel:
        return self._add_to_cache(
            self.settings.channels,
            self.settings.max_channels_store,
            self.channels, channel
        )
    
    def update_guilds(self, guild: Guild) -> Guild:
        for c in guild.channels: self.update_channels(c)
        for t in guild.threads: self.update_channels(t)
        return self._add_to_cache(
            self.settings.guilds,
            self.settings.max_guilds_store,
            self.guilds, guild
        )


    def _get_from_cache[T: Cachable](self, cache: dict[int, CacheEntry[T]], id: int) -> T | None:
        return item.data if (item := cache.get(id)) is not None else None

    def get_user(self, user_id: int) -> User | None:
        return self._get_from_cache(self.users, user_id)
    
    def get_message(self, message_id: int) -> Message | None:
        return self._get_from_cache(self.messages, message_id)

    def get_channel(self, channel_id: int) -> Channel | None:
        return self._get_from_cache(self.channels, channel_id)

    def get_guild(self, guild_id: int) -> Guild | None:
        return self._get_from_cache(self.guilds, guild_id)


    def _remove_from_cache[T: Cachable](self, cache: dict[int, CacheEntry[T]], id: int) -> T | None:
        return o.data if (o := cache.pop(id, None)) else None

    def remove_user(self, user_id: int) -> User | None:
        return self._remove_from_cache(self.users, user_id)
    
    def remove_message(self, message_id: int) -> Message | None:
        return self._remove_from_cache(self.messages, message_id)

    def remove_channel(self, channel_id: int) -> Channel | None:
        return self._remove_from_cache(self.channels, channel_id)

    def remove_guild(self, guild_id: int) -> Guild | None:
        return self._remove_from_cache(self.guilds, guild_id)


    async def _cleanup_cache[T: Cachable](self, cache: dict[int, CacheEntry[T]]):
        while True:
            now = datetime.now()
            threshold = now - self.settings.invalidation_time
            to_remove: list[int] = []
            for id, item in cache.items():
                if item.created_at < threshold:
                    to_remove.append(id)
                else:
                    break

            for i in to_remove:
                cache.pop(i, None)
            
            await asyncio.sleep(self.settings.cleanup_interval.total_seconds())