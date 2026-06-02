import asyncio
import logging
import inspect
from collections.abc import Callable, Coroutine
from typing import Any

import aiohttp

from .cache import CacheSettings, CacheStorage
from .enums.event_dispatch import Event
from .errors import ImproperToken, Unauthorized
from .flags import IntentFlags
from .gateway import GatewayClient
from .http import HTTPClient, Path
from .managers import ChannelManager, GuildManager, MessageManager, UserManager

__all__ = (
    "Bot",
)

_log = logging.getLogger(__name__)

type CoroFunc = Callable[..., Coroutine[Any, Any, Any]]

class ApplicationCommandCallbackData:
    ":meta private:"

    __slots__ = (
        "description",
        "callback"
    )
    
    def __init__(self, description: str, callback: CoroFunc):
        self.description = description
        self.callback = callback

class Bot:
    """
    Represents a Discord Bot.
    
    Parameters
    ----------
    intents : :class:`IntentFlags <dispy.flags.IntentFlags>`
        The IntentFlags to be passed to the GatewayClient.
    cache_settings : :class:`CacheSettings <dispy.cache.CacheSettings>`, optional
        The CacheSettings for managing the Cache System of the Bot instance. Defaults to ``CacheSettings()``
    """
    
    intents: IntentFlags
    "The IntentFlags to be passed to the :class:`GatewayClient <dispy.gateway.GatewayClient>`."
    
    http: HTTPClient
    "The HTTPClient used for the REST API."
    
    gateway: GatewayClient
    "The GatewayClient that manages the Gateway Connection."
    
    users: UserManager
    "The UserManager used to fetch User objects."
    
    messages: MessageManager
    "The MessageManager used to fetch Message objects."
    
    channels: ChannelManager
    "The ChannelManager used to fetch Channel objects."
    
    guilds: GuildManager
    "The GuildManager used to fetch Guild objects."
    
    __slots__ = (
        "intents",
        "http",
        "gateway",
        "_listeners",
        "_command_callbacks",
        "_storage",
        "users",
        "messages",
        "channels",
        "guilds",
        "_session"
    )
    
    def __init__(
        self, *,
        intents: IntentFlags,
        cache_settings: CacheSettings = CacheSettings()
    ):
        self.intents = intents
        self.http = HTTPClient()
        self._listeners: dict[str, list[CoroFunc]] = {}
        self._command_callbacks: dict[str, ApplicationCommandCallbackData] = {}

        self._storage = CacheStorage(cache_settings)
        self.users = UserManager(self.http, self._storage)
        self.messages = MessageManager(self.http, self._storage)
        self.channels = ChannelManager(self.http, self._storage)
        self.guilds = GuildManager(self.http, self._storage)
        
        self._session: aiohttp.ClientSession | None = None

    def run(self, token: str) -> None:
        """
        A synchronous method to start a event loop and run the :meth:`Bot.start()` method.
        
        Parameters
        ----------
        token : :class:`str`
            The bot token used to authenticate with discord. Do not prefix this, the library will handle prefixing.        

        Raises
        ------
        :class:`ImproperToken`
            An improper token was passed.
        """
        asyncio.run(self.start(token))
        
    async def _verify_token(self) -> None:
        try:
            await self.http.request(Path("GET", "users/@me"))
        except Unauthorized:
            raise ImproperToken(401, "Improper token has been passed.")

    async def start(self, token: str) -> None:
        """
        Verifies the token and connects to the gateway.
        
        Parameters
        ----------
        token : :class:`str`
            The bot token used to authenticate with discord. Do not prefix this, the library will handle prefixing.
            
        Raises
        ------
        :class:`ImproperToken`
            An improper token was passed.
        """
        try:
            if self._storage.settings.cache_invalidation: self._storage.start_cleanup_tasks()
            self._session = aiohttp.ClientSession(
                "https://discord.com/api/v10/",
                headers={
                    "Authorization": f"Bot {token}"
                }
            )
            self.http._session = self._session
            _log.debug("Attempting to verify token (length=%s)", len(token))
            await self._verify_token()
            _log.debug("Verified token successfully.")
            self.gateway = GatewayClient(self, self._session, token, self.intents)
            await self.gateway.connect()
            await self.gateway.wait_until_closed()
        except asyncio.CancelledError:
            raise
        finally:
            await self.stop()

    async def stop(self) -> None:
        """
        Disconnects the gateway and closes the session.
        """
        try:
            if self.gateway:
                await self.gateway.close()
        finally:
            if self._session:
                await self._session.close()

    def listen(self, event: Event | None = None):
        """
        This function is a decotstor.
        
        Registers an asynchronous listener for a gateway event.
        
        Parameters
        ----------
        event : :class:`Event <dispy.enums.event_dispatch.Event>` | :class:`None`, optional
            The Gateway Event to listen to. Defaults to name of function in format such as ``on_interaction_create``. Defaults to ``None``
            
        Raises
        ------
        :class:`TypeError`
            The decorator was applied to a synchronous function.
                    
        Examples
        --------
        Registering based on the function name:
        
        .. code-block:: python
        
            @bot.listen()
            async def on_message_create(message: dispy.Message) -> None:
                ...
        
        Explicitly passing event name:
        
        .. code-block:: python
        
            @bot.listen(dispy.Event.MESSAGE_CREATE)
            async def can_be_named_anything(message: dispy.Message) -> None:
                ...
        """
        def decorator(func: CoroFunc) -> CoroFunc:
            if not inspect.iscoroutinefunction(func): raise TypeError(f"Event listener '{func.__name__}' has to be a coroutine function.")
            self._listeners.setdefault(event.value if event is not None else func.__name__, []).append(func)
            return func
        return decorator
        
    def command(self, *, name: str, description: str):
        """
        This function is a decorator.
        
        Registers a command callback for a slash (application) command.

        Parameters
        ----------
        name : :class:`str`
            The name of the application command.
        description : :class:`str`
            The description of the application command.
            
        Raises
        ------
        :class:`TypeError`
            The decorator was applied to a synchronous function.
        """
        def decorator(func: CoroFunc) -> CoroFunc:
            if not inspect.iscoroutinefunction(func): raise TypeError(f"Command callback for '{name}:{func.__name__}' has to be a coroutine function.")
            self._command_callbacks[name] = ApplicationCommandCallbackData(description, func)
            return func
        return decorator