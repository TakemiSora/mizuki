import aiohttp
import asyncio
import logging
import inspect

from typing import overload

from mizuki.cache import CacheSettings, CacheStorage
from mizuki.enums.event_dispatch import Event
from mizuki.state import ConnectionState
from mizuki.errors import ImproperToken, Unauthorized
from mizuki.flags import IntentFlags
from mizuki.gateway import GatewayClient
from mizuki.http import HTTPClient, Path
from mizuki._utils import _MISSING, CoroFunc, CoroDecorator

from mizuki.enums.command import ApplicationCommandType
from mizuki.enums.interaction import InteractionContextType, ApplicationIntegrationType

from mizuki.objects.command import PartialApplicationCommand, Localization
from mizuki.objects.user import User
from mizuki.objects.permissions import Permissions

from mizuki.managers.channel import ChannelManager
from mizuki.managers.guild import GuildManager
from mizuki.managers.message import MessageManager
from mizuki.managers.user import UserManager
from mizuki.managers.command import CommandManager

__all__ = (
    "Bot",
)

_log = logging.getLogger(__name__)

class Bot:
    """
    Represents a Discord Bot.

    Parameters
    ----------
    intents : :class:`IntentFlags <mizuki.flags.IntentFlags>`
        The IntentFlags to be passed to the GatewayClient.

    cache_settings : :class:`CacheSettings <mizuki.cache.CacheSettings>`, optional
        The CacheSettings for managing the Cache System of the Bot instance. Defaults to ``CacheSettings()``
    """

    intents: IntentFlags
    "The IntentFlags to be passed to the :class:`GatewayClient <mizuki.gateway.GatewayClient>`."

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
        "_state",
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
        cache_settings: CacheSettings | None = None
    ):
        self.intents = intents
        self._listeners: dict[str, list[CoroFunc]] = {}
        self._setup_hook: CoroFunc | None = None
        self._commands_data: dict[str, tuple[int, PartialApplicationCommand]] = {}
        self._storage = CacheStorage(cache_settings or CacheSettings())
        self._state = ConnectionState()
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
            return User(await self.http.request(
                Path(
                    "GET",
                    "users/@me"
                )
            ), state=self._state)
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
            if self._storage.settings.cache_invalidation:
                self._storage.start_cleanup_tasks()

            self.http = self._state.init_http(token)
            self._session = self.http._session

            _log.debug("Attempting to verify token (length=%s)", len(token))
            self.user = await self._verify_token()
            _log.info("Verified token successfully.")

            managers = self._state.init_managers(
                cache_storage=self._storage,
                application_id=self.user.id,
                commands_data=self._commands_data
            )
            self.users = managers.users
            self.channels = managers.channels
            self.messages = managers.messages
            self.commands = managers.commands
            self.guilds = managers.guilds

            self.gateway = await self._state.init_gateway(
                bot=self,
                token=token,
                intents=self.intents
            )
            if self._setup_hook is not None:
                await self._setup_hook()
            await self.gateway.wait_until_closed()

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
        event : :class:`Event <mizuki.enums.event_dispatch.Event>` | :class:`None`, optional
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
            async def on_message_create(message: mizuki.Message) -> None:
                ...

        Explicitly passing event name:

        .. code-block:: python

            @bot.listen(mizuki.Event.MESSAGE_CREATE)
            async def can_be_named_anything(message: mizuki.Message) -> None:
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