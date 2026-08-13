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
    CoroDecorator,
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
    __slots__ = ("name", "name_localizations", "value")

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
        return assign_val(
            cls(CommandChoicePayload(name=name, value=value)),
            name_localizations=name_localizations,
        )

    def _to_dict(self) -> CommandChoicePayload:
        return assign_val_dict(
            CommandChoicePayload(name=self.name, value=self.value),
            name_localizations=mtd(self.name_localizations),
        )


class ApplicationCommandOption:
    _SLASH_COMMAND_OPTION_TYPE_MAP: dict[Any, CommandOptionType] = {  # noqa: RUF012
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

    _VALID_TYPES = list(_SLASH_COMMAND_OPTION_TYPE_MAP)  # noqa: RUF012

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
        self.options = [ApplicationCommandOption(a) for a in data.get("options", [])]
        self.channel_types = (
            [ChannelType(c) for c in d]
            if (d := data.get("channel_types")) is not None
            else None
        )
        self.min_value = data.get("min_value")
        self.max_value = data.get("max_value")
        self.min_length = data.get("min_length")
        self.max_length = data.get("max_length")
        self.autocomplete = data.get("autocomplete")

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
        options: list[ApplicationCommandOption] = _MISSING,
        channel_types: list[ChannelType] = _MISSING,
        min_value: int | float = _MISSING,  # noqa: PYI041
        max_value: int | float = _MISSING,  # noqa: PYI041
        min_length: int = _MISSING,
        max_length: int = _MISSING,
        autocomplete: bool = _MISSING,
    ) -> Self:
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
            options=options,
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
                raise TypeError(f"Parameter type must be one of: {cls._VALID_TYPES}")

        option_type = cls._SLASH_COMMAND_OPTION_TYPE_MAP.get(param_type)
        if option_type is None:
            raise TypeError(f"Parameter type must be one of: {cls._VALID_TYPES}")

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
            options=[o._to_dict() for o in self.options] if self.options else None,
            channel_types=[ct.value for ct in self.channel_types]
            if self.channel_types
            else None,
            min_value=self.min_value,
            max_value=self.max_value,
            min_length=self.min_length,
            max_length=self.max_length,
            autocomplete=self.autocomplete,
        )


class PartialApplicationCommand:
    __slots__ = (
        "_autocompletor",
        "_callback",
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

    _callback: Callable[..., Coroutine[Any, Any, Any]]

    def __init__(self, data: PartialApplicationCommandPayload):
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

    @classmethod
    def new(
        cls,
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
        callback: CoroFunc = _MISSING,
        autocompletor: Callable[
            [Interaction, ApplicationCommandData], Coroutine[Any, Any, Any]
        ] = _MISSING,
    ) -> Self:
        return assign_val(
            cls(
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
            _callback=callback,
            autocompletor=autocompletor,
        )

    @classmethod
    def _from_command(
        cls,
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
        autocompletor: Callable[
            [Interaction, ApplicationCommandData], Coroutine[Any, Any, Any]
        ] = _MISSING,
    ) -> Self:
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

        return cls.new(
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
            callback=func,
            autocompletor=autocompletor,
        )

    def _to_dict(self) -> PartialApplicationCommandPayload:
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
            integration_types=[i.value for i in self.integration_types]
            if self.integration_types
            else None,
            contexts=[c.value for c in self.contexts] if self.contexts else None,
        )


class ApplicationCommand(PartialApplicationCommand):
    __slots__ = (
        "application_id",
        "guild_id",
        "handler",
        "id",
        "version",
    )

    def __init__(self, data: ApplicationCommandPayload):
        super().__init__(data)
        self.id = Snowflake(data["id"])
        self.application_id = Snowflake(data["application_id"])
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.version = Snowflake._from_str(data.get("version"))
        self.handler = scls(CommandHandler, data.get("handler"))


class SubCommand:
    type: CommandOptionType = CommandOptionType.SUB_COMMAND

    __slots__ = (
        "_callback",
        "description",
        "description_localizations",
        "name",
        "name_localizations",
        "options",
    )

    _callback: Callable[..., Coroutine[Any, Any, Any]]

    def __init__(self, data: ApplicationCommandOptionPayload) -> None:
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
        callback: Callable[..., Coroutine[Any, Any, Any]] = _MISSING,
    ) -> SubCommand:
        return assign_val(
            cls({"type": cls.type.value, "name": name, "description": description}),
            name_localizations=name_localizations,
            description_localizations=description_localizations,
            options=options,
            _callback=callback,
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

        return cls.new(
            name=name,
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            callback=func,
        )


class NestedApplicationCommandGroup:
    type: CommandOptionType = CommandOptionType.SUB_COMMAND_GROUP

    __slots__ = (
        "description",
        "description_localizations",
        "name",
        "name_localizations",
        "options",
    )

    name: str
    name_localizations: Localization | None
    description: str
    description_localizations: Localization | None
    options: list[SubCommand]

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
        self, data_options: list[ApplicationCommandDataOption]
    ) -> tuple[Callable[..., Coroutine[Any, Any, Any]], ApplicationCommandDataOption]:
        for option in self.options:
            if option.name == data_options[0].name:
                return getattr(option, "_callback", None), data_options[0].options

    def command(
        self,
        *,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
    ) -> CoroDecorator:
        def decorator(func: CoroFunc) -> CoroFunc:
            if not inspect.iscoroutinefunction(func):
                raise TypeError(
                    f"Command callback for '{name}:{func.__name__}' has to be a coroutine function."
                )

            self.options.append(
                SubCommand._from_function(
                    func,
                    name=name,
                    name_localizations=name_localizations,
                    description=description,
                    description_localizations=description_localizations,
                )
            )

            return func

        return decorator

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


class PartialApplicationCommandGroup:
    type: ApplicationCommandType = ApplicationCommandType.CHAT_INPUT

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

    def command(
        self,
        *,
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
    ) -> CoroDecorator:
        def decorator(func: CoroFunc) -> CoroFunc:
            if not inspect.iscoroutinefunction(func):
                raise TypeError(
                    f"Command callback for '{name}:{func.__name__}' has to be a coroutine function."
                )

            self.options.append(
                SubCommand._from_function(
                    func,
                    name=name,
                    name_localizations=name_localizations,
                    description=description,
                    description_localizations=description_localizations,
                )
            )

            return func

        return decorator

    def _get_response_data(
        self, data_options: tuple[ApplicationCommandDataOption, ...]
    ) -> tuple[
        Callable[..., Coroutine[Any, Any, Any]] | None,
        tuple[ApplicationCommandDataOption, ...],
    ]:
        for option in self.options:
            if option.name == data_options[0].name:
                if isinstance(option, SubCommand):
                    return getattr(option, "_callback", None), data_options[0].options
                else:
                    return option._get_response_data(data_options[0].options)

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
    __slots__ = (
        "application_id",
        "guild_id",
        "handler",
        "id",
        "version",
    )

    def __init__(self, data: ApplicationCommandPayload):
        super().__init__(data)
        self.id = Snowflake(data["id"])
        self.application_id = Snowflake(data["application_id"])
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.version = Snowflake._from_str(data.get("version"))
        self.handler = scls(CommandHandler, data.get("handler"))
