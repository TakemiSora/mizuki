from __future__ import annotations

import inspect
import types
from typing import get_origin, get_args, cast

from typing import Any, Literal, Self, overload

from mizuki._utils import (
    _MISSING,
    assign_val,
    assign_val_dict,
    mtd,
    scls,
    sint,
    CoroFunc,
)
from mizuki.enums.channel import ChannelType
from mizuki.enums.command import (
    ApplicationCommandType,
    CommandHandler,
    CommandOptionType,
)
from mizuki.enums.interaction import ApplicationIntegrationType, InteractionContextType
from mizuki.payloads.command import (
    ApplicationCommandPayload,
    BaseApplicationCommandPayload,
    CommandChoicePayload,
    CommandOptionPayload,
    LocalizationPayload,
    PartialApplicationCommandPayload,
)
from mizuki.objects.permissions import Permissions
from mizuki.objects.snowflake import Snowflake

from mizuki.objects.user import User
from mizuki.objects.channel import PartialGuildChannel, PartialThreadChannel
from mizuki.objects.role import Role

__all__ = (
    "Mentionable",
    "Localization",
    "ApplicationCommandOption",
    "ApplicationCommandChoice",
    "PartialApplicationCommand",
    "ApplicationCommand",
)


class Mentionable: ...


class Localization:
    __slots__ = (
        "id",
        "da",
        "de",
        "en_gb",
        "en_us",
        "es_es",
        "es_419",
        "fr",
        "hr",
        "it",
        "lt",
        "hu",
        "nl",
        "no",
        "pl",
        "pt_br",
        "ro",
        "fi",
        "sv_se",
        "vi",
        "tr",
        "cs",
        "el",
        "bg",
        "ru",
        "uk",
        "hi",
        "th",
        "zh_cn",
        "ja",
        "zh_tw",
        "ko",
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
        value: str | int | float,
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

    __slots__ = (
        "type",
        "name",
        "name_localizations",
        "description",
        "description_localizations",
        "required",
        "choices",
        "options",
        "channel_types",
        "min_value",
        "max_value",
        "min_length",
        "max_length",
        "autocomplete",
    )

    def __init__(self, data: CommandOptionPayload):
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
        type: Literal[
            CommandOptionType.SUB_COMMAND, CommandOptionType.SUB_COMMAND_GROUP
        ],
        name: str,
        name_localizations: Localization = _MISSING,
        description: str,
        description_localizations: Localization = _MISSING,
        options: list[ApplicationCommandOption] = _MISSING,
    ) -> Self: ...

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
        min_value: int | float = _MISSING,
        max_value: int | float = _MISSING,
        min_length: int = _MISSING,
        max_length: int = _MISSING,
        autocomplete: bool = _MISSING,
    ) -> Self:
        return assign_val(
            cls(
                CommandOptionPayload(
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
            CommandOptionPayload(
                type=option_type.value,
                name=param.name,
                description="...",
                required=param.default is inspect.Parameter.empty,
            )
        )

    def _to_dict(self) -> CommandOptionPayload:
        return assign_val_dict(
            CommandOptionPayload(
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


class BaseApplicationCommand:
    __slots__ = (
        "type",
        "name",
        "name_localizations",
        "description_localizations",
        "options",
        "nsfw",
        "integration_types",
        "contexts",
    )

    def __init__(self, data: BaseApplicationCommandPayload):
        self.type = ApplicationCommandType(data.get("type", 1))
        self.name = data["name"]
        self.name_localizations = scls(Localization, data.get("name_localizations"))
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


class PartialApplicationCommand(BaseApplicationCommand):
    __slots__ = ("description", "default_member_permissions", "_callback")

    def __init__(
        self, data: PartialApplicationCommandPayload, callback: CoroFunc | None
    ):
        super().__init__(data)
        self.description = data.get("description")
        self.default_member_permissions = scls(
            Permissions, sint(data.get("default_member_permissions"))
        )
        self._callback = callback

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
    ) -> Self:
        return assign_val(
            cls(PartialApplicationCommandPayload(name=name, type=type.value), callback),
            name_localizations=name_localizations,
            description=description,
            description_localizations=description_localizations,
            options=options,
            default_member_permissions=default_member_permissions,
            integration_types=integration_types,
            contexts=contexts,
            nsfw=nsfw,
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
    ) -> Self:
        parameters = list(inspect.signature(func).parameters.values())
        options: list[ApplicationCommandOption] = []
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
        )

    def _to_dict(self) -> PartialApplicationCommandPayload:
        return assign_val_dict(
            PartialApplicationCommandPayload(
                name=self.name, type=self.type.value, nsfw=self.nsfw
            ),
            name_localizations=mtd(self.name_localizations),
            description=self.description,
            description_localizations=mtd(self.description_localizations),
            options=[o._to_dict() for o in self.options] if self.options else None,
            default_member_permissions=self.default_member_permissions.value
            if self.default_member_permissions
            else None,
            integration_types=[i.value for i in self.integration_types]
            if self.integration_types
            else None,
            contexts=[c.value for c in self.contexts] if self.contexts else None,
        )


class ApplicationCommand(BaseApplicationCommand):
    __slots__ = (
        "id",
        "description",
        "application_id",
        "version",
        "handler",
        "guild_id",
    )

    def __init__(self, data: ApplicationCommandPayload):
        super().__init__(data)
        self.id = Snowflake(data["id"])
        self.description = data["description"]
        self.application_id = Snowflake(data["application_id"])
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.version = Snowflake._from_str(data.get("version"))
        self.handler = scls(CommandHandler, data.get("handler"))
