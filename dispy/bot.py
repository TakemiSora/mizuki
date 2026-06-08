import asyncio

import logging
import inspect
from typing import overload

import aiohttp

from .cache import CacheSettings, CacheStorage
from .enums.event_dispatch import Event
from .errors import ImproperToken, Unauthorized
from .flags import IntentFlags
from .gateway import GatewayClient
from .http import HTTPClient
from ._utils import _MISSING, CoroFunc, CoroDecorator

from .enums.command import ApplicationCommandType
from .enums.interaction import InteractionContextType, ApplicationIntegrationType

from .objects.command import PartialApplicationCommand, Localization, ApplicationCommandOption
from .objects.user import User
from .objects.permissions import Permissions

from .managers.channel import ChannelManager
from .managers.guild import GuildManager
from .managers.message import MessageManager
from .managers.user import UserManager
from .managers.command import CommandManager

__all__ = (
    "Bot",
)

_log = logging.getLogger(__name__)

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
    "The UserManager used to managers User objects."
    
    messages: MessageManager
    "The MessageManager used to manage Message objects."
    
    channels: ChannelManager
    "The ChannelManager used to manage Channel objects."
    
    guilds: GuildManager
    "The GuildManager used to manage Guild objects."
    
    commands: CommandManager
    "The CommandManager used to manage Commands."
    
    user: User
    "The User object of the bot."
    
    __slots__ = (
        "intents",
        "http",
        "gateway",
        "_listeners",
        "_setup_hook",
        "_commands_data",
        "_storage",
        "users",
        "messages",
        "channels",
        "guilds",
        "commands",
        "user",
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
        self._setup_hook: CoroFunc | None = None
        self._commands_data: dict[str, tuple[int, PartialApplicationCommand]] = {}

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
        
    async def _verify_token(self) -> User:
        try:
            return await self.users.fetch_me()
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
            self.user = await self._verify_token()
            _log.info("Verified token successfully.")
            self.commands = CommandManager(self.http, self._storage, self.user.id, self._commands_data)
            self.gateway = GatewayClient(self, self._session, token, self.intents)
            await self.gateway.connect()
            if self._setup_hook is not None:
                await self._setup_hook()
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

    def listen(self, event: Event | None = None) -> CoroDecorator:
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
        
    def setup(self) -> CoroDecorator:
        """
        This function is a decorator.
        
        Registers a setup hook which runs once after connecting to the gateway.
        
        Raises
        ------
        :class:`TypeError`
            The decorator was applied to a synchronous function.
        """
        def decorator(func: CoroFunc) -> CoroFunc:
            if not inspect.iscoroutinefunction(func): raise TypeError(f"Setup hook '{func.__name__}' has to be a coroutine function.")
            self._setup_hook = func
            return func
        return decorator

    @overload
    def command(
        self, *,
        guild_id: int,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        default_member_permissions: Permissions = _MISSING,
        nsfw: bool = False
    ) -> CoroDecorator: ...

    @overload
    def command(
        self, *,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        default_member_permissions: Permissions = _MISSING,
        integration_types: list[ApplicationIntegrationType] = _MISSING,
        contexts: list[InteractionContextType] = _MISSING,
        nsfw: bool = False
    ) -> CoroDecorator: ...
        
    def command(
        self, *,
        guild_id: int | None = None,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        default_member_permissions: Permissions = _MISSING,
        integration_types: list[ApplicationIntegrationType] = _MISSING,
        contexts: list[InteractionContextType] = _MISSING,
        nsfw: bool = False
    ) -> CoroDecorator:
        """
        This function is a decorator.
        
        Registers a command callback for a slash (application) command.

        Parameters
        ----------
        name : :class:`str`
            The name of the application command.
        description : :class:`str`, optional
            The description of the application command.
            
        Raises
        ------
        :class:`TypeError`
            The decorator was applied to a synchronous function.
        """
        def decorator(func: CoroFunc) -> CoroFunc:
            if not inspect.iscoroutinefunction(func): raise TypeError(f"Command callback for '{name}:{func.__name__}' has to be a coroutine function.")
            
            self._commands_data[name] = guild_id or 0, PartialApplicationCommand._from_command(
                func,
                name=name,
                name_localizations=name_localizations,
                description=description,
                description_localizations=description_localizations,
                default_member_permissions=default_member_permissions,
                integration_types=integration_types,
                contexts=contexts,
                type=ApplicationCommandType.CHAT_INPUT,
                nsfw=nsfw
            )

            return func

        return decorator