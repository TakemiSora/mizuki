from __future__ import annotations

import inspect
import types
from collections.abc import Callable, Coroutine
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Self,
    get_args,
    get_origin,
    overload,
)

from mizuki._utils import (
    _MISSING,
    CoroFunc,
    JSONPayload,
    assign_val,
    assign_val_dict,
    maybe_iter,
    mtd,
    scls,
    sint,
)
from mizuki.enums.channel import ChannelType
from mizuki.enums.command import (
    ApplicationCommandType,
    CommandHandler,
    CommandOptionType,
)
from mizuki.enums.interaction import ApplicationIntegrationType, InteractionContextType
from mizuki.objects.channel import PartialGuildChannel, PartialThreadChannel
from mizuki.objects.permissions import Permissions
from mizuki.objects.role import Role
from mizuki.objects.snowflake import Snowflake
from mizuki.objects.user import User
from mizuki.payloads.command import (
    ApplicationCommandOptionPayload,
    ApplicationCommandPayload,
    CommandChoicePayload,
    LocalizationPayload,
    PartialApplicationCommandPayload,
)

if TYPE_CHECKING:
    from mizuki.objects.interaction import (
        ApplicationCommandData,
        ApplicationCommandDataOption,
        Interaction,
    )

__all__ = (
    "ApplicationCommand",
    "ApplicationCommandChoice",
    "ApplicationCommandGroup",
    "ApplicationCommandOption",
    "Localization",
    "Mentionable",
    "PartialApplicationCommand",
    "PartialApplicationCommandGroup",
    "SubCommand",
)


class Mentionable: ...


class Localization:
    __slots__ = (
        "bg",
        "cs",
        "da",
        "de",
        "el",
        "en_gb",
        "en_us",
        "es_419",
        "es_es",
        "fi",
        "fr",
        "hi",
        "hr",
        "hu",
        "id",
        "it",
        "ja",
        "ko",
        "lt",
        "nl",
        "no",
        "pl",
        "pt_br",
        "ro",
        "ru",
        "sv_se",
        "th",
        "tr",
        "uk",
        "vi",
        "zh_cn",
        "zh_tw",
    )

    def __init__(self, data: LocalizationPayload) -> None:
        self.id = data.get("id")
        self.da = data.get("da")
        self.de = data.get("de")
        self.en_gb = data.get("en-GB")
        self.en_us = data.get("en-US")
        self.es_es = data.get("es-ES")
        self.es_419 = data.get("es-419")
        self.fr = data.get("fr")
        self.hr = data.get("hr")
        self.it = data.get("it")
        self.lt = data.get("lt")
        self.hu = data.get("hu")
        self.nl = data.get("nl")
        self.no = data.get("no")
        self.pl = data.get("pl")
        self.pt_br = data.get("pt-BR")
        self.ro = data.get("ro")
        self.fi = data.get("fi")
        self.sv_se = data.get("sv-SE")
        self.vi = data.get("vi")
        self.tr = data.get("tr")
        self.cs = data.get("cs")
        self.el = data.get("el")
        self.bg = data.get("bg")
        self.ru = data.get("ru")
        self.uk = data.get("uk")
        self.hi = data.get("hi")
        self.th = data.get("th")
        self.zh_cn = data.get("zh-CN")
        self.ja = data.get("ja")
        self.zh_tw = data.get("zh-TW")
        self.ko = data.get("ko")

    def _to_dict(self) -> LocalizationPayload:
        return LocalizationPayload(**{k: getattr(self, k) for k in self.__slots__})


class ApplicationCommandChoice:
    """Represents a choice in an application command parameter for the user to select."""

    __slots__ = ("name", "name_localizations", "value")

    name: str
    "The name of the choice."

    name_localizations: Localization | None
    "The localizations for the name of the choice."

    value: str | int | float
    "The value of the choice."

    def __init__(self, data: CommandChoicePayload):
        self.name = data["name"]
        self.name_localizations = scls(Localization, data.get("name_localizations"))
        self.value = data["value"]

    @classmethod
    def new(
        cls,
        *,
        name: str,
        name_localizations: Localization = _MISSING,
        value: str | int | float,  # noqa: PYI041
    ) -> Self:
        """Returns an instance of an ApplicationCommand choice.

        Parameters
        ----------
        name : :class:`str`
            The name of the choice.

        name_localizations : :class:`Localization`, optional
            The localizations for the name of the choice.

        value : :class:`str` | :class:`int` | :class:`float`
            The value of the choice.
        """
        return assign_val(
            cls(CommandChoicePayload(name=name, value=value)),
            name_localizations=name_localizations,
        )

    def _to_dict(self) -> CommandChoicePayload:
        return assign_val_dict(
            CommandChoicePayload(name=self.name, value=self.value),
            name_localizations=mtd(self.name_localizations),
        )


_SLASH_COMMAND_OPTION_TYPE_MAP: dict[Any, CommandOptionType] = {
    str: CommandOptionType.STRING,
    int: CommandOptionType.INTEGER,
    bool: CommandOptionType.BOOLEAN,
    float: CommandOptionType.NUMBER,
    User: CommandOptionType.USER,
    Role: CommandOptionType.ROLE,
    PartialGuildChannel: CommandOptionType.CHANNEL,
    PartialThreadChannel: CommandOptionType.CHANNEL,
    Mentionable: CommandOptionType.MENTIONABLE,
}

_VALID_TYPES = list(_SLASH_COMMAND_OPTION_TYPE_MAP)


class ApplicationCommandOption:
    """Represents an application command option/parameter."""

    __slots__ = (
        "autocomplete",
        "channel_types",
        "choices",
        "description",
        "description_localizations",
        "max_length",
        "max_value",
        "min_length",
        "min_value",
        "name",
        "name_localizations",
        "options",
        "required",
        "type",
    )

    type: CommandOptionType
    "The type of the option."

    name: str
    "The name of the option."

    name_localizations: Localization | None
    "The localizations for the name of the option."

    description: str
    "The description of the option."

    description_localizations: Localization | None
    "The localizations for the description of the option."

    required: bool
    "Whether this option is required."

    choices: list[ApplicationCommandChoice]
    "The list of choices for the user to select from for this parameter."

    channel_types: list[ChannelType] | None
    "The channel types to limit the selection of a channel object to."

    min_value: float | int | None
    "The minimum value the user can enter for an integer or a float."

    max_value: float | int | None
    "The maximum value the user can enter for an integer or a float."

    min_length: int | None
    "The minimum amount of characters the user can enter for a string."

    max_length: int | None
    "The maximum amount of characters the user can enter for a string."

    autocomplete: bool
    "Whether the option is autocompletable."

    def __init__(self, data: ApplicationCommandOptionPayload):
        self.type = CommandOptionType(data["type"])
        self.name = data["name"]
        self.name_localizations = scls(Localization, data.get("name_localizations"))
        self.description = data["description"]
        self.description_localizations = scls(
            Localization, data.get("description_localizations")
        )
        self.required = data.get("required", False)
        self.choices = [ApplicationCommandChoice(a) for a in data.get("choices", [])]
        self.channel_types = (
            [ChannelType(c) for c in d]
            if (d := data.get("channel_types")) is not None
            else None
        )
        self.min_value = data.get("min_value")
        self.max_value = data.get("max_value")
        self.min_length = data.get("min_length")
        self.max_length = data.get("max_length")
        self.autocomplete = data.get("autocomplete", False)

    @overload
    @classmethod
    def new(
        cls,
        *,
        type: Literal[CommandOptionType.STRING],
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        required: bool = False,
        choices: list[ApplicationCommandChoice] = _MISSING,
        min_length: int = _MISSING,
        max_length: int = _MISSING,
        autocomplete: bool = _MISSING,
    ) -> Self: ...

    @overload
    @classmethod
    def new(
        cls,
        *,
        type: Literal[CommandOptionType.INTEGER],
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        required: bool = False,
        choices: list[ApplicationCommandChoice] = _MISSING,
        min_value: int = _MISSING,
        max_value: int = _MISSING,
        autocomplete: bool = _MISSING,
    ) -> Self: ...

    @overload
    @classmethod
    def new(
        cls,
        *,
        type: Literal[
            CommandOptionType.BOOLEAN,
            CommandOptionType.USER,
            CommandOptionType.ROLE,
            CommandOptionType.MENTIONABLE,
            CommandOptionType.ATTACHMENT,
        ],
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        required: bool = False,
    ) -> Self: ...

    @overload
    @classmethod
    def new(
        cls,
        *,
        type: Literal[CommandOptionType.CHANNEL],
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        required: bool = False,
        channel_types: list[ChannelType] = _MISSING,
    ) -> Self: ...

    @overload
    @classmethod
    def new(
        cls,
        *,
        type: Literal[CommandOptionType.NUMBER],
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        required: bool = False,
        choices: list[ApplicationCommandChoice] = _MISSING,
        min_value: float = _MISSING,
        max_value: float = _MISSING,
        autocomplete: bool = _MISSING,
    ) -> Self: ...

    @classmethod
    def new(
        cls,
        *,
        type: CommandOptionType,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        required: bool = False,
        choices: list[ApplicationCommandChoice] = _MISSING,
        channel_types: list[ChannelType] = _MISSING,
        min_value: int | float = _MISSING,  # noqa: PYI041
        max_value: int | float = _MISSING,  # noqa: PYI041
        min_length: int = _MISSING,
        max_length: int = _MISSING,
        autocomplete: bool = _MISSING,
    ) -> Self:
        """Returns an instance of an application command option.

        Parameters
        ----------
        type : :class:`CommandOptionType <mizuki.enums.command.CommandOptionType>`
            The type of the option.

        name : :class:`str`
            The name of the option.

        name_localizations : :class:`Localization`, optional
            The localizations for the name of the option.

        description : :class:`str`
            The description of the option.

        description_localizations : :class:`Localization`, optional
            The localizations for the description of the option.

        required : :class:`bool`, optional
            Whether this option is required.

        choices : list[:class:`ApplicationCommandChoice`], optional
            The choices for the user to select from, valid for INTEGER, STRING and NUMBER types.

        channel_types : list[:class:`ChannelType <mizuki.enums.channel.ChannelType>`], optional
            The channel types the user is limited to when selecting a channel, valid for CHANNEL types.

        min_value : :class:`int` | :class:`float`, optional
            The minimum value the user can enter, valid for INTEGER and NUMBER types.

        max_values : :class:`int` | :class:`float`, optional
            The maximum value the user can enter, valid for INTEGER and NUMBER types.

        min_length : :class:`int`, optional
            The minimum amount of characters the user must enter, valid for STRING types.

        max_values : :class:`int`, optional
            The maximum amount of characters the user can enter, valid for STRING types.

        autocomplete : :class:`bool`, optional
            Whether this field will send autocomplete requests, valid for INTEGER, STRING and NUMBER types.
        """
        return assign_val(
            cls(
                ApplicationCommandOptionPayload(
                    type=type.value,
                    name=name,
                    description=description,
                    required=required,
                )
            ),
            name_localizations=name_localizations,
            description_localizations=description_localizations,
            choices=choices,
            channel_types=channel_types,
            min_value=min_value,
            max_value=max_value,
            min_length=min_length,
            max_length=max_length,
            autocomplete=autocomplete,
        )

    @classmethod
    def _from_function_param(cls, param: inspect.Parameter) -> Self:
        annotation = param.annotation
        origin = get_origin(annotation)
        match origin:
            case types.UnionType:
                union = [t for t in get_args(annotation) if t is not types.NoneType]
                # exclude NoneType as user may use it for default such as str | None = None

                if len(union) > 1:
                    raise TypeError(
                        f"Parameter type must be a concrete type or an optional type (T | None). Provided: {annotation}"
                    )

                param_type = union[0]
            case None:
                param_type = annotation
            case _:
                raise TypeError(f"Parameter type must be one of: {_VALID_TYPES}")

        option_type = _SLASH_COMMAND_OPTION_TYPE_MAP.get(param_type)
        if option_type is None:
            raise TypeError(f"Parameter type must be one of: {_VALID_TYPES}")

        return cls(
            ApplicationCommandOptionPayload(
                type=option_type.value,
                name=param.name,
                description="...",
                required=param.default is inspect.Parameter.empty,
            )
        )

    def _to_dict(self) -> ApplicationCommandOptionPayload:
        return assign_val_dict(
            ApplicationCommandOptionPayload(
                type=self.type.value,
                name=self.name,
                description=self.description,
                required=self.required,
            ),
            name_localizations=mtd(self.name_localizations),
            description_localizations=mtd(self.description_localizations),
            choices=[c._to_dict() for c in self.choices] if self.choices else None,
            channel_types=(
                [ct.value for ct in self.channel_types] if self.channel_types else None
            ),
            min_value=self.min_value,
            max_value=self.max_value,
            min_length=self.min_length,
            max_length=self.max_length,
            autocomplete=self.autocomplete or None,
        )


type AutocompletorCallback = Callable[
    [
        Interaction[ApplicationCommandData],
        dict[str, ApplicationCommandDataOption],
    ],
    Coroutine[Any, Any, Any],
]

type CommandResponseData = tuple[
    CoroFunc | None,
    AutocompletorCallback | None,
    ApplicationCommandDataOption.AnyApplicationCommandDataOptions,
]


class CallbackAndAutocompletorSettable:
    __slots__ = ("_autocompletor", "_callback")

    _autocompletor: AutocompletorCallback | None
    _callback: CoroFunc | None

    name: str

    def set_callback(self, callback: CoroFunc) -> Self:
        """Sets the callback method for this application command.

        Parameters
        ----------
        callback : `async (Interaction[ApplicationCommandData], ...) -> Any`
            The callback for the command.

        Raises
        ------
        :class:`TypeError`
            The callback provided was a synchronous function.
        """

        if not inspect.iscoroutinefunction(callback):
            raise TypeError(
                f"Command callback for '{self.name}:{callback.__name__}' has to be a coroutine function."
            )

        self._callback = callback
        return self

    def callback(self) -> Callable[[CoroFunc], CoroFunc]:
        """Sets the callback method for this application command.

        This method is a decorator.

        This decorator should be applied to a method with the following signature:

            `async (Interaction[ApplicationCommandData], ...) -> Any`

        Raises
        ------
        :class:`TypeError`
            The callback provided was a synchronous function.
        """

        def decorator(func: CoroFunc) -> CoroFunc:
            self.set_callback(func)
            return func

        return decorator

    def set_autocompletor(self, autocompletor: AutocompletorCallback) -> Self:
        """Sets the autocompletor method for this application command.

        Parameters
        ----------
        autocompletor : `async (Interaction[ApplicationCommandData], dict[str, ApplicationCommandDataOption]) -> Any`
            The autocompletor callback for the command.

        Raises
        ------
        :class:`TypeError`
            The autocompletor provided was a synchronous function.
        """

        if not inspect.iscoroutinefunction(autocompletor):
            raise TypeError(
                f"Command autocompletor for '{self.name}:{autocompletor.__name__}' has to be a coroutine function.'"
            )

        self._autocompletor = autocompletor
        return self

    def autocompletor(self) -> Callable[[AutocompletorCallback], AutocompletorCallback]:
        """Sets the autocompletor method for this application command.

        This method is a decorator.

        This decorator should be applied to a method with the following signature:

            `async (Interaction[ApplicationCommandData], dict[str, ApplicationCommandDataOption]) -> Any`

        Raises
        ------
        :class:`TypeError`
            The autocompletor provided was a synchronous function.
        """

        def decorator(func: AutocompletorCallback) -> AutocompletorCallback:
            self.set_autocompletor(func)
            return func

        return decorator


class PartialApplicationCommand(CallbackAndAutocompletorSettable):
    """Represents a locally initialized application command."""

    __slots__ = (
        "contexts",
        "default_member_permissions",
        "description",
        "description_localizations",
        "integration_types",
        "name",
        "name_localizations",
        "nsfw",
        "options",
        "type",
    )

    type: ApplicationCommandType
    "The type of the command."

    name: str
    "The name of the command."

    name_localizations: Localization | None
    "The localizations for the name of the command."

    description: str
    "The description of the command."

    description_localizations: Localization | None
    "The localizations for the description of the command."

    options: list[ApplicationCommandOption]
    "The options/parameters of the command."

    nsfw: bool
    "Whether the command is NSFW."

    integration_types: list[ApplicationIntegrationType]
    "The installation contexts where this globally-scoped command is available."

    contexts: list[InteractionContextType] | None
    "The interaction contexts where this globally-scoped command can be used."

    default_member_permissions: Permissions | None
    "The default permissions that are required to use this command."

    def __init__(self, data: PartialApplicationCommandPayload):
        self._autocompletor = None
        self._callback = None

        self.type = ApplicationCommandType(data.get("type", 1))
        self.name = data["name"]
        self.name_localizations = scls(Localization, data.get("name_localizations"))
        self.description = data["description"]
        self.description_localizations = scls(
            Localization, data.get("description_localizations")
        )
        self.options = [ApplicationCommandOption(a) for a in data.get("options", [])]
        self.nsfw = data.get("nsfw", False)
        self.integration_types = [
            ApplicationIntegrationType(a) for a in data.get("integration_types", [])
        ]
        self.contexts = (
            [InteractionContextType(i) for i in d]
            if (d := data.get("contexts")) is not None
            else None
        )
        self.default_member_permissions = scls(
            Permissions, data["default_member_permissions"]
        )

    @staticmethod
    def new(
        *,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str = _MISSING,
        description_localizations: Localization = _MISSING,
        options: list[ApplicationCommandOption] = _MISSING,
        default_member_permissions: Permissions = _MISSING,
        integration_types: list[ApplicationIntegrationType] = _MISSING,
        contexts: list[InteractionContextType] = _MISSING,
        type: ApplicationCommandType = ApplicationCommandType.CHAT_INPUT,
        nsfw: bool = False,
    ) -> PartialApplicationCommand:
        """Returns a locally intialized/partial application command.

        Parameters
        ----------
        type : :class:`ApplicationCommandType <mizuki.enums.command.ApplicationCommandType>`, optional
            The type of the command to create.

        guild_id : :class:`int` | :class:`None`, optional
            The ID of the guild if registering the command to be guild-specific.

        name : :class:`str`
            The name of the application command.

        name_localizations : :class:`Localization`, optional
            The localizations for the name of the application command.

        description : :class:`str`, optional
            The description of the application command.

        description_localizations : :class:`Localization`, optional
            The localizations for the description of the application command.

        options: list[:class:`ApplicationCommandOption`], optional
            The options/parameters for the command.

        default_member_permisssions: :class:`Permissions <mizuki.objects.permissions.Permissions>`, optional
            The default permissions that are required to use this command.

        integration_types : list[:class:`ApplicationIntegrationType <mizuki.enums.interaction.ApplicationIntegrationType>`], optional
            The installation contexts where this command is available, only allowed for globally-scoped commands.

        contexts : list[:class:`InteractionContextType <mizuki.enums.interaction.InteractionContextType>`], optional
            The interaction contexts where this command can be used, only allowed for globally-scoped commands.

        nsfw : :class:`bool`, optional
            Whether this command is age-restricted.

        """
        return assign_val(
            PartialApplicationCommand(
                {
                    "type": type.value,
                    "name": name,
                    "description": description or "",
                    "default_member_permissions": getattr(
                        default_member_permissions, "value", None
                    ),
                }
            ),
            name_localizations=name_localizations,
            description_localizations=description_localizations,
            options=options,
            integration_types=integration_types,
            contexts=contexts,
            nsfw=nsfw,
        )

    @staticmethod
    def _from_command(
        func: CoroFunc,
        *,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str = _MISSING,
        description_localizations: Localization = _MISSING,
        default_member_permissions: Permissions = _MISSING,
        integration_types: list[ApplicationIntegrationType] = _MISSING,
        contexts: list[InteractionContextType] = _MISSING,
        type: ApplicationCommandType = ApplicationCommandType.CHAT_INPUT,
        nsfw: bool = False,
        autocompletor: AutocompletorCallback = _MISSING,
    ) -> PartialApplicationCommand:
        options: list[ApplicationCommandOption] = []

        if type is ApplicationCommandType.CHAT_INPUT:
            parameters = list(inspect.signature(func).parameters.values())
            command_options: dict[str, ApplicationCommandOption] = getattr(
                func, "__command_options__", {}
            )

            for param in parameters[1:]:
                if param.annotation is inspect.Parameter.empty:
                    raise ValueError(
                        f"No type hint for slash command '{name}', function={func.__name__}: '{param.name}'"
                    )

                if param.name in command_options:
                    options.append(command_options[param.name])
                else:
                    options.append(ApplicationCommandOption._from_function_param(param))

        command = PartialApplicationCommand.new(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            default_member_permissions=default_member_permissions,
            integration_types=integration_types,
            contexts=contexts,
            type=type,
            nsfw=nsfw,
        ).set_callback(func)

        if autocompletor:
            command.set_autocompletor(autocompletor)

        return command

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "type": self.type.value,
                "name": self.name,
                "description": self.description,
                "default_member_permissions": getattr(
                    self.default_member_permissions, "value", None
                ),
            },
            name_localizations=mtd(self.name_localizations),
            description_localizations=mtd(self.description_localizations),
            options=[o._to_dict() for o in self.options] if self.options else None,
            integration_types=(
                [i.value for i in self.integration_types]
                if self.integration_types
                else None
            ),
            contexts=[c.value for c in self.contexts] if self.contexts else None,
        )

    def _get_response_data(
        self,
        data_options: ApplicationCommandDataOption.AnyApplicationCommandDataOptions,
    ) -> CommandResponseData:
        return self._callback, self._autocompletor, data_options


class ApplicationCommand(PartialApplicationCommand):
    """Represents a full/fetched application command."""

    __slots__ = (
        "application_id",
        "guild_id",
        "handler",
        "id",
        "version",
    )

    id: Snowflake
    "The ID of the command."

    application_id: Snowflake
    "The ID of the application the command is associated with."

    guild_id: Snowflake | None
    "The ID of the guild if the command is guild-specific."

    version: Snowflake
    "The autoincrementing version identifier for the command."

    handler: CommandHandler | None
    "Determines whether the interaction is handled by the app's interactions or by Discord."

    def __init__(self, data: ApplicationCommandPayload):
        super().__init__(data)
        self.id = Snowflake(data["id"])
        self.application_id = Snowflake(data["application_id"])
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.version = Snowflake(data["version"])
        self.handler = scls(CommandHandler, data.get("handler"))


class SubCommand(CallbackAndAutocompletorSettable):
    """Represents a subcommand in command group."""

    __slots__ = (
        "description",
        "description_localizations",
        "name",
        "name_localizations",
        "options",
    )

    type: Literal[CommandOptionType.SUB_COMMAND] = CommandOptionType.SUB_COMMAND
    "The type of the option, always `CommandOptionType.SUB_COMMAND`."

    name: str
    "The name of the command."

    name_localizations: Localization | None
    "The localizations for the name of the command."

    description: str
    "The description of the command."

    description_localizations: Localization | None
    "The localizations for the description of the command."

    options: list[ApplicationCommandOption]
    "The options/parameters of the command."

    def __init__(self, data: ApplicationCommandOptionPayload) -> None:
        self._autocompletor = None
        self._callback = None

        self.name = data["name"]
        self.name_localizations = scls(Localization, data.get("name_localizations"))
        self.description = data["description"]
        self.description_localizations = scls(
            Localization, data.get("description_localizations")
        )
        self.options = [ApplicationCommandOption(o) for o in data.get("options", [])]

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "type": self.type.value,
                "name": self.name,
                "description": self.description,
                "options": maybe_iter(self.options),
            },
            name_localizations=mtd(self.name_localizations),
            description_localizations=mtd(self.description_localizations),
        )

    @classmethod
    def new(
        cls,
        *,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        options: list[ApplicationCommandOption] = _MISSING,
    ) -> SubCommand:
        """Returns a locally intialized subcommand.

        Parameters
        ----------
        name : :class:`str`
            The name of the application command.

        name_localizations : :class:`Localization`, optional
            The localizations for the name of the application command.

        description : :class:`str`, optional
            The description of the application command.

        description_localizations : :class:`Localization`, optional
            The localizations for the description of the application command.

        options: list[:class:`ApplicationCommandOption`], optional
            The options/parameters for the command.
        """
        return assign_val(
            cls({"type": cls.type.value, "name": name, "description": description}),
            name_localizations=name_localizations,
            description_localizations=description_localizations,
            options=options,
        )

    @classmethod
    def _from_function(
        cls,
        func: CoroFunc,
        *,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        autocompletor: AutocompletorCallback = _MISSING,
    ) -> SubCommand:
        options: list[ApplicationCommandOption] = []

        parameters = list(inspect.signature(func).parameters.values())
        command_options: dict[str, ApplicationCommandOption] = getattr(
            func, "__command_options__", {}
        )

        for param in parameters[1:]:
            if param.annotation is inspect.Parameter.empty:
                raise ValueError(
                    f"No type hint for slash command '{name}', function={func.__name__}: '{param.name}'"
                )

            if param.name in command_options:
                options.append(command_options[param.name])
            else:
                options.append(ApplicationCommandOption._from_function_param(param))

        subcommand = cls.new(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
        ).set_callback(func)

        if autocompletor:
            subcommand.set_autocompletor(autocompletor)

        return subcommand


class SubCommandAddable:
    options: list[SubCommand | NestedApplicationCommandGroup] | list[SubCommand]

    def command(
        self,
        *,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        autocompletor: AutocompletorCallback = _MISSING,
    ) -> Callable[[CoroFunc], SubCommand]:
        """Creates a subcommand in the command group.

        This method is a decorator and transforms the method into a :class:`SubCommand`.

        This decorator should be applied to a function with the following signature:

            `async (Interaction[ApplicationCommandData], ...) -> Any`

        Parameters
        ----------
        name : :class:`str`
            The name of the application command.

        name_localizations : :class:`Localization`, optional
            The localizations for the name of the application command.

        description : :class:`str`, optional
            The description of the application command.

        description_localizations : :class:`Localization`, optional
            The localizations for the description of the application command.

        autocompletor : `async (Interaction[ApplicationCommandData], dict[str, ApplicationCommandDataOption]) -> Any`
            The autocompletor for the command.
        """

        def decorator(func: CoroFunc) -> SubCommand:
            command = SubCommand._from_function(
                func,
                name=name,
                name_localizations=name_localizations,
                description=description,
                description_localizations=description_localizations,
                autocompletor=autocompletor,
            )

            self.options.append(command)

            return command

        return decorator


class NestedApplicationCommandGroup(SubCommandAddable):
    """Represents a command group nested inside a command group."""

    __slots__ = (
        "description",
        "description_localizations",
        "name",
        "name_localizations",
        "options",
    )

    type: Literal[CommandOptionType.SUB_COMMAND_GROUP] = (
        CommandOptionType.SUB_COMMAND_GROUP
    )
    "The type of the option, always `CommandOptionType.SUB_COMMAND_GROUP`."

    name: str
    "The name of the command group."

    name_localizations: Localization | None
    "The localizations for the name of the command group."

    description: str
    "The description of the command group."

    description_localizations: Localization | None
    "The localizations for the description of the command group."

    options: list[SubCommand]
    "The list of subcommands of this group."

    def __init__(self, data: ApplicationCommandOptionPayload) -> None:
        self.name = data["name"]
        self.name_localizations = scls(Localization, data.get("name_localizations"))
        self.description = data["description"]
        self.description_localizations = scls(
            Localization, data.get("description_localizations")
        )
        self.options = [SubCommand(o) for o in data.get("options", [])]

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "type": self.type.value,
                "name": self.name,
                "description": self.description,
                "options": maybe_iter(self.options),
            },
            name_localizations=mtd(self.name_localizations),
            description_localizations=mtd(self.description_localizations),
        )

    def _get_response_data(
        self,
        data_options: ApplicationCommandDataOption.AnyApplicationCommandDataOptions,
    ) -> CommandResponseData:
        callback = None
        autocompletor = None

        for option in self.options:
            if option.name == data_options[0].name:
                callback = option._callback
                autocompletor = option._autocompletor

        return callback, autocompletor, data_options[0].options

    @classmethod
    def new(
        cls,
        *,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        options: list[SubCommand] = _MISSING,
    ) -> NestedApplicationCommandGroup:
        """Returns an instance of a sub command group.

        Parameters
        ----------
        name : :class:`str`
            The name of the sub command group.

        name_localizations : :class:`Localization`, optional
            The localizations for the name of the sub command group.

        description : :class:`str`
            The description of the sub command group.

        description_localizations : :class:`Localization`, optional
            The localizations for the description of the sub command group.

        options : list[:class:`SubCommand`], optional
            The commands of the sub command group.
        """
        return assign_val(
            cls(
                {
                    "type": cls.type.value,
                    "name": name,
                    "description": description,
                }
            ),
            name_localizations=name_localizations,
            description_localizations=description_localizations,
            options=options,
        )


class PartialApplicationCommandGroup(SubCommandAddable):
    """Represents a locally initialized/partial application command group."""

    __slots__ = (
        "contexts",
        "default_member_permissions",
        "description",
        "description_localizations",
        "integration_types",
        "name",
        "name_localizations",
        "nsfw",
        "options",
    )

    type: Literal[ApplicationCommandType.CHAT_INPUT] = ApplicationCommandType.CHAT_INPUT
    "The type of the command group, always `ApplicationCommandType.CHAT_INPUT`."

    name: str
    "The name of the command group."

    name_localizations: Localization | None
    "The localizations for the name of the command group."

    description: str
    "The description of the command group."

    description_localizations: Localization | None
    "The localizations for the description of the command group."

    options: list[SubCommand | NestedApplicationCommandGroup]
    "The subcommands/subcommand groups of the command group."

    nsfw: bool
    "Whether the commands in the command group are NSFW."

    integration_types: list[ApplicationIntegrationType]
    "The installation contexts where the commands in this globally-scoped command group are available."

    contexts: list[InteractionContextType] | None
    "The interaction contexts where the commands in this globally-scoped command group can be used."

    default_member_permissions: Permissions | None
    "The default permissions that are required to use the commands in the command group."

    def __init__(self, data: PartialApplicationCommandPayload) -> None:
        self.name = data["name"]
        self.name_localizations = scls(Localization, data.get("name_localizations"))
        self.description = data.get("description", "")
        self.description_localizations = scls(
            Localization, data.get("description_localizations")
        )
        self.options: list[NestedApplicationCommandGroup | SubCommand] = []
        for option in data.get("options", []):
            if option["type"] == CommandOptionType.SUB_COMMAND:
                self.options.append(SubCommand(option))
            elif option["type"] == CommandOptionType.SUB_COMMAND_GROUP:
                self.options.append(NestedApplicationCommandGroup(option))
        self.nsfw = data.get("nsfw", False)
        self.integration_types = [
            ApplicationIntegrationType(a) for a in data.get("integration_types", [])
        ]
        self.contexts = (
            [InteractionContextType(i) for i in d]
            if (d := data.get("contexts")) is not None
            else None
        )
        self.default_member_permissions = scls(
            Permissions, sint(data.get("default_member_permissions"))
        )

    def _to_dict(self) -> JSONPayload:
        return assign_val_dict(
            {
                "type": self.type.value,
                "name": self.name,
                "description": self.description,
                "default_member_permissions": getattr(
                    self.default_member_permissions, "value", None
                ),
            },
            name_localizations=mtd(self.name_localizations),
            description_localizations=mtd(self.description_localizations),
            options=maybe_iter(self.options),
            nsfw=self.nsfw,
            integration_types=[i.value for i in self.integration_types]
            if self.integration_types
            else None,
            contexts=(
                maybe_iter(self.contexts, lambda x: x.value) if self.contexts else None
            ),
        )

    def _get_response_data(
        self,
        data_options: ApplicationCommandDataOption.AnyApplicationCommandDataOptions,
    ) -> CommandResponseData:
        callback = None
        autocompletor = None

        for option in self.options:
            if option.name == data_options[0].name:
                if isinstance(option, SubCommand):
                    callback = option._callback
                    autocompletor = option._autocompletor
                else:
                    return option._get_response_data(data_options[0].options)

        return callback, autocompletor, data_options[0].options

    @staticmethod
    def new(
        *,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        options: list[NestedApplicationCommandGroup | SubCommand] = _MISSING,
        default_member_permissions: Permissions = _MISSING,
        integration_types: list[ApplicationIntegrationType] = _MISSING,
        contexts: list[InteractionContextType] = _MISSING,
        nsfw: bool = False,
    ) -> PartialApplicationCommandGroup:
        """Returns an instance of a locally intialized/partial application command group.

        Parameters
        ----------
        name : :class:`str`
            The name of the command group.

        name_localizations : :class:`Localization`, optional
            The localizations for the name of the command group.

        description : :class:`str`
            The description of the command group.

        description_localizations : :class:`Localization`, optional
            The localizations for the description of the command group.

        options : list[:class:`NestedApplicationCommandGroup` | :class:`SubCommand`], optional
            The commands/sub command groups of the command group.

        default_member_permissions : :class:`Permissions <mizuki.objects.permissions.Permissions>`, optional
            The default permissions required to use the commands in this command group.

        integration_types : list[:class:`ApplicationIntegrationType`], optional
            The installation contexts where the commands in this globally-scoped command group are available.

        contexts : list[:class:`InteractionContextType`], optional
            The interaction contexts where the commands in this globally-scoped command group can be used.

        nsfw : :class:`bool`, optional
            Whether the commands in this command group are age-restricted.
        """
        return assign_val(
            PartialApplicationCommandGroup(
                {
                    "type": ApplicationCommandType.CHAT_INPUT.value,
                    "name": name,
                    "description": description,
                    "default_member_permissions": getattr(
                        default_member_permissions, "value", None
                    ),
                },
            ),
            name_localizations=name_localizations,
            description_localizations=description_localizations,
            options=options,
            integration_types=integration_types,
            contexts=contexts,
            nsfw=nsfw,
        )

    def create_subgroup(
        self,
        *,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        options: list[SubCommand] = _MISSING,
    ) -> NestedApplicationCommandGroup:
        """Creates a sub command group and adds it to the command group

        Parameters
        ----------
        name : :class:`str`
            The name of the sub command group.

        name_localizations : :class:`Localization`, optional
            The localizations for the name of the sub command group.

        description : :class:`str`
            The description of the sub command group.

        description_localizations : :class:`Localization`, optional
            The localizations for the description of the sub command group.

        options : list[:class:`SubCommand`], optional
            The commands of the sub command group.
        """
        subgroup = NestedApplicationCommandGroup.new(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
        )

        self.options.append(subgroup)

        return subgroup

    @property
    def commands(self) -> list[NestedApplicationCommandGroup | SubCommand]:
        return self.options


class ApplicationCommandGroup(PartialApplicationCommandGroup):
    """Returns a full/fetched application command group."""

    __slots__ = (
        "application_id",
        "guild_id",
        "handler",
        "id",
        "version",
    )

    id: Snowflake
    "The ID of the command group."

    application_id: Snowflake
    "The ID of the application the command group is associated with."

    guild_id: Snowflake | None
    "The ID of the guild if the command is guild-specific."

    version: Snowflake
    "The autoincrementing version identifier for the command."

    handler: CommandHandler | None
    "Determines whether the interaction is handled by the app's interactions or by Discord."

    def __init__(self, data: ApplicationCommandPayload):
        super().__init__(data)
        self.id = Snowflake(data["id"])
        self.application_id = Snowflake(data["application_id"])
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.version = Snowflake(data["version"])
        self.handler = scls(CommandHandler, data.get("handler"))


def parse_application_command(
    data: ApplicationCommandPayload,
) -> ApplicationCommand | ApplicationCommandGroup:
    if (options := data.get("options")) and options[0]["type"] in (
        CommandOptionType.SUB_COMMAND,
        CommandOptionType.SUB_COMMAND_GROUP,
    ):
        return ApplicationCommandGroup(data)
    return ApplicationCommand(data)
