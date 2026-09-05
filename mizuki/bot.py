import asyncio
import inspect
import logging
from collections.abc import Callable
from datetime import timedelta
from typing import Literal, overload

import aiohttp

from mizuki._utils import _MISSING, CoroDecorator, CoroFunc
from mizuki.cache import CacheSettings, CacheStorage
from mizuki.enums.command import ApplicationCommandType
from mizuki.enums.event_dispatch import Event
from mizuki.enums.interaction import ApplicationIntegrationType, InteractionContextType
from mizuki.errors import ImproperToken, Unauthorized
from mizuki.flags import IntentFlags
from mizuki.gateway import GatewayClient
from mizuki.http import HTTPClient, Path
from mizuki.managers.channel import ChannelManager
from mizuki.managers.command import CommandManager
from mizuki.managers.guild import GuildManager
from mizuki.managers.message import MessageManager
from mizuki.managers.role import RoleManager
from mizuki.managers.user import UserManager
from mizuki.objects.command import (
    AutocompletorCallback,
    Localization,
    PartialApplicationCommand,
    PartialApplicationCommandGroup,
)
from mizuki.objects.permissions import Permissions
from mizuki.objects.user import User
from mizuki.state import ConnectionState

__all__ = ("Bot",)

_log = logging.getLogger(__name__)


class Bot:
    """
    Represents a Discord Bot.

    Parameters
    ----------
    intents : :class:`~mizuki.IntentFlags`
        The IntentFlags to be passed to the GatewayClient.

    cache_settings : :class:`~mizuki.CacheSettings`, optional
        The CacheSettings for managing the Cache System of the Bot instance. Defaults to ``CacheSettings()``
    """

    intents: IntentFlags
    "The IntentFlags to be passed to the gateway."

    http: HTTPClient
    "The HTTPClient used for the REST API."

    gateway: GatewayClient
    "The GatewayClient that manages the Gateway Connection."

    user: User
    "The User object of the bot."

    __slots__ = (
        "_commands_data",
        "_listeners",
        "_session",
        "_setup_hook",
        "_state",
        "_storage",
        "gateway",
        "http",
        "intents",
        "user",
    )

    def __init__(
        self,
        *,
        intents: IntentFlags,
        cache_settings: CacheSettings | None = None,
        default_component_timeout: timedelta | None = None,
        default_modal_timeout: timedelta | None = None,
    ) -> None:
        self.intents = intents
        self._listeners: dict[str, list[CoroFunc]] = {}
        self._setup_hook: CoroFunc | None = None
        self._commands_data: dict[
            str, tuple[int, PartialApplicationCommand | PartialApplicationCommandGroup]
        ] = {}
        self._storage = CacheStorage(cache_settings or CacheSettings())
        self._state = ConnectionState(
            default_component_timeout=default_component_timeout,
            default_modal_timeout=default_modal_timeout,
        )
        self._session: aiohttp.ClientSession | None = None

    @property
    def channels(self) -> ChannelManager:
        """The manager used to manage channels."""
        return self._state.managers.channels

    @property
    def commands(self) -> CommandManager:
        """The manager used to manage commands."""
        return self._state.managers.commands

    @property
    def guilds(self) -> GuildManager:
        """The manager used to manage guilds."""
        return self._state.managers.guilds

    @property
    def messages(self) -> MessageManager:
        """The manager used to manage messages."""
        return self._state.managers.messages

    @property
    def roles(self) -> RoleManager:
        """The manager used to manage roles."""
        return self._state.managers.roles

    @property
    def users(self) -> UserManager:
        """The manager used to manage users."""
        return self._state.managers.users
    

    def run(self, token: str) -> None:
        """A synchronous method to start a event loop and run the :meth:`Bot.start()` method.

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
            return User(
                await self.http.request(Path("GET", "users/@me")), state=self._state
            )
        except Unauthorized:
            raise ImproperToken("Improper token has been passed.")

    async def start(self, token: str) -> None:
        """Verifies the token and connects to the gateway.

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
            self._state.start_cleanup_tasks()

            self.http = self._state.init_http(token)
            self._session = self._state.session

            _log.debug("Attempting to verify token (length=%s)", len(token))
            self.user = await self._verify_token()
            _log.info("Verified token successfully.")

            self._state.init_managers(
                cache_storage=self._storage,
                application_id=self.user.id,
                commands_data=self._commands_data,
            )

            self.gateway = await self._state.init_gateway(
                bot=self, token=token, intents=self.intents
            )
            if self._setup_hook is not None:
                await self._setup_hook()
            await self.gateway.wait_until_closed()

        finally:
            await self.stop()

    async def stop(self) -> None:
        """Disconnects the gateway and closes the session."""
        try:
            if self.gateway:
                await self.gateway.close()
        finally:
            if self._session:
                await self._session.close()

    def listen(self, event: Event | None = None) -> CoroDecorator:
        """Registers an asynchronous listener for a gateway event.

        This function is a decorator.

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
            if not inspect.iscoroutinefunction(func):
                raise TypeError(
                    f"Event listener '{func.__name__}' has to be a coroutine function."
                )
            self._listeners.setdefault(
                event.value if event is not None else func.__name__, []
            ).append(func)
            return func

        return decorator

    def setup(self) -> CoroDecorator:
        """Registers a setup hook which runs once after connecting to the gateway.

        This method is a decorator.

        This decorator should be applied to a method with the following signature:

            `async () -> Any`

        Raises
        ------
        :class:`TypeError`
            The decorator was applied to a synchronous function.
        """

        def decorator(func: CoroFunc) -> CoroFunc:
            if not inspect.iscoroutinefunction(func):
                raise TypeError(
                    f"Setup hook '{func.__name__}' has to be a coroutine function."
                )
            self._setup_hook = func
            return func

        return decorator

    def register_command(
        self,
        command: PartialApplicationCommand | PartialApplicationCommandGroup,
        *,
        guild_id: int | None = None,
    ) -> None:
        """Registers an application command or an application command group in this bot instance.

        .. note::

            This does not sync your commands to Discord!
            Use :method:`CommandManager.sync_all() <mizuki.managers.command.CommandManager.sync_all>` to sync all registered commands.

        Parameters
        ----------
        command : :class:`PartialApplicationCommand <mizuki.objects.command.PartialApplicationCommand>` | :class:`PartialApplicationCommandGroup <mizuki.objects.command.PartialApplicationCommandGroup>`
            The command/group to register.

        guild_id : :class:`int` | :class:`None`, optional
            The guild ID to register the command
        """
        self._commands_data[command.name] = guild_id or 0, command

    @overload
    def command(
        self,
        *,
        type: Literal[
            ApplicationCommandType.CHAT_INPUT
        ] = ApplicationCommandType.CHAT_INPUT,
        guild_id: int,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        default_member_permissions: Permissions = _MISSING,
        nsfw: bool = False,
        autocompletor: AutocompletorCallback = _MISSING,
    ) -> Callable[[CoroFunc], PartialApplicationCommand]: ...

    @overload
    def command(
        self,
        *,
        type: Literal[
            ApplicationCommandType.CHAT_INPUT
        ] = ApplicationCommandType.CHAT_INPUT,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        default_member_permissions: Permissions = _MISSING,
        integration_types: list[ApplicationIntegrationType] = _MISSING,
        contexts: list[InteractionContextType] = _MISSING,
        nsfw: bool = False,
        autocompletor: AutocompletorCallback = _MISSING,
    ) -> Callable[[CoroFunc], PartialApplicationCommand]: ...

    @overload
    def command(
        self,
        *,
        type: Literal[ApplicationCommandType.USER, ApplicationCommandType.MESSAGE],
        name: str,
        name_localizations: Localization = _MISSING,
        default_member_permissions: Permissions = _MISSING,
        integration_types: list[ApplicationIntegrationType] = _MISSING,
        contexts: list[InteractionContextType] = _MISSING,
        nsfw: bool = False,
    ) -> Callable[[CoroFunc], PartialApplicationCommand]: ...

    @overload
    def command(
        self,
        *,
        type: Literal[ApplicationCommandType.USER, ApplicationCommandType.MESSAGE],
        guild_id: int,
        name: str,
        name_localizations: Localization = _MISSING,
        default_member_permissions: Permissions = _MISSING,
        nsfw: bool = False,
    ) -> Callable[[CoroFunc], PartialApplicationCommand]: ...

    def command(
        self,
        *,
        type: ApplicationCommandType = ApplicationCommandType.CHAT_INPUT,
        guild_id: int | None = None,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str = _MISSING,
        description_localizations: Localization = _MISSING,
        default_member_permissions: Permissions = _MISSING,
        integration_types: list[ApplicationIntegrationType] = _MISSING,
        contexts: list[InteractionContextType] = _MISSING,
        nsfw: bool = False,
        autocompletor: AutocompletorCallback = _MISSING,
    ) -> Callable[[CoroFunc], PartialApplicationCommand]:
        """Creates an applciation command object and registers the function the decorator is applied on as the callback for the command.

        This decorator transforms the function into a :class:`PartialApplicationCommand <mizuki.objects.command.PartialApplicationCommand>` object.

        This decorator should be applied to a method with the following signature:

            `async (Interaction[ApplicationCommandData], ...) -> Any`

        Parameters
        ----------
        type : :class:`ApplicationCommandType <mizuki.enums.command.ApplicationCommandType>`, optional
            The type of the command to create.

        guild_id : :class:`int` | :class:`None`, optional
            The ID of the guild if registering the command to be guild-specific.

        name : :class:`str`
            The name of the application command.

        name_localizations : :class:`Localization <mizuki.objects.command.Localization>`, optional
            The localizations for the name of the application command.

        description : :class:`str`, optional
            The description of the application command.

        description_localizations : :class:`Localization <mizuki.objects.command.Localization>`, optional
            The localizations for the description of the application command.

        default_member_permisssions: :class:`Permissions <mizuki.objects.permissions.Permissions>`, optional
            The default permissions that are required to use this command.

        integration_types : list[:class:`ApplicationIntegrationType <mizuki.enums.interaction.ApplicationIntegrationType>`], optional
            The installation contexts where this command is available, only allowed for globally-scoped commands.

        contexts : list[:class:`InteractionContextType <mizuki.enums.interaction.InteractionContextType>`], optional
            The interaction contexts where this command can be used, only allowed for globally-scoped commands.

        nsfw : :class:`bool`, optional
            Whether this command is age-restricted.

        autocompletor : `async (Interaction[ApplicationCommandData], dict[str, ApplicationCommandDataOption]) -> Any`, optional
            The autocompletor callback for the command.

        Raises
        ------
        :class:`TypeError`
            The decorator was applied to a synchronous function.

        Examples
        --------

        Chat Input (Slash) Commands:

        .. code-block:: python

            @bot.command(
                name="chat-input-command",
                description="This is a chat input command!"
            )
            async def _(interaction: mizuki.Interaction, some_parameter: str) -> None:
                await interaction.response.send_response("Hello!")


        User Context Commands:

        .. code-block:: python

            @bot.command(
                type=mizuki.ApplicationCommandType.USER,
                name="user-context-command"
            )
            async def _(
                interaction: mizuki.Interaction,
                user: mizuki.User, # The user this command targeted, always present
                member: mizuki.ResolvedMember | None, # The member object for the guild, if it was ran in a guild
            ) -> None:
                await interaction.response.send_response(f"Hello, {user}!")


        Message Context Commands:

        .. code-block:: python

            @bot.command(
                type=mizuki.ApplicationCommandType.MESSAGE,
                name="message-context-command"
            )
            async def _(
                interaction: mizuki.Interaction,
                message: mizuki.Message, # The targeted message
            ) -> None:
                await interaction.response.send_response(f"Hello, <@{message.author.id}>!")


        """

        def decorator(func: CoroFunc) -> PartialApplicationCommand:
            command = PartialApplicationCommand._from_command(
                func,
                name=name,
                name_localizations=name_localizations,
                description=description,
                description_localizations=description_localizations,
                default_member_permissions=default_member_permissions,
                integration_types=integration_types,
                contexts=contexts,
                type=type,
                nsfw=nsfw,
                autocompletor=autocompletor,
            )

            self.register_command(command, guild_id=guild_id)

            return command

        return decorator

    def create_command_group(
        self,
        *,
        guild_id: int | None = None,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        default_member_permissions: Permissions = _MISSING,
        integration_types: list[ApplicationIntegrationType] = _MISSING,
        contexts: list[InteractionContextType] = _MISSING,
        nsfw: bool = False,
    ) -> PartialApplicationCommandGroup:
        """Creates an application command group and registers it to the bot instance.

        Parameters
        ----------
        guild_id : :class:`int` | :class:`None`, optional
            The ID of the guild if registering the command to be guild-specific.

        name : :class:`str`
            The name of the application command.

        name_localizations : :class:`Localization <mizuki.objects.command.Localization>`, optional
            The localizations for the name of the application command.

        description : :class:`str`, optional
            The description of the application command.

        description_localizations : :class:`Localization <mizuki.objects.command.Localization>`, optional
            The localizations for the description of the application command.

        default_member_permisssions: :class:`Permissions <mizuki.objects.permissions.Permissions>`, optional
            The default permissions that are required to use this command.

        integration_types : list[:class:`ApplicationIntegrationType <mizuki.enums.interaction.ApplicationIntegrationType>`], optional
            The installation contexts where this command is available, only allowed for globally-scoped commands.

        contexts : list[:class:`InteractionContextType <mizuki.enums.interaction.InteractionContextType>`], optional
            The interaction contexts where this command can be used, only allowed for globally-scoped commands.

        nsfw : :class:`bool`, optional
            Whether this command is age-restricted.
        """

        subgroup = PartialApplicationCommandGroup.new(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            default_member_permissions=default_member_permissions,
            integration_types=integration_types,
            contexts=contexts,
            nsfw=nsfw,
        )

        self.register_command(subgroup, guild_id=guild_id)

        return subgroup
