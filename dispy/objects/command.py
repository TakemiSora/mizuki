from __future__ import annotations

from typing import Any, Self
from collections.abc import Callable, Coroutine

from ..enums.channel import ChannelType
from ..enums.command import ApplicationCommandType, CommandHandler, CommandOptionType
from ..enums.interaction import ApplicationIntegrationType, InteractionContextType
from ..payloads.command import (
    BaseApplicationCommandPayload,
    PartialApplicationCommandPayload,
    ApplicationCommandPayload,
    CommandChoicePayload,
    CommandOptionPayload,
    LocalizationPayload,
)
from .._utils import scls, mtd, sint, _MISSING, assign_val, assign_val_dict
from .permissions import Permissions
from .snowflake import Snowflake

__all__ = (
    "Localization",
    "ApplicationCommandOption",
    "ApplicationCommandChoice",
    "PartialApplicationCommand",
    "ApplicationCommand"
)

class Localization:
    __slots__ = (
        "id", "da", "de", "en_gb", "en_us",
        "es_es", "es_419", "fr", "hr", "it",
        "lt", "hu", "nl", "no", "pl", "pt_br",
        "ro", "fi", "sv_se", "vi", "tr", "cs",
        "el", "bg", "ru", "uk", "hi", "th",
        "zh_cn", "ja", "zh_tw", "ko",
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
    __slots__ = (
        "name",
        "name_localizations",
        "value"
    )

    def __init__(self, data: CommandChoicePayload):
        self.name = data["name"]
        self.name_localizations = scls(Localization, data.get("name_localizations"))
        self.value = data["value"]

    @classmethod
    def new(
        cls, *,
        name: str,
        name_localizations: Localization = _MISSING,
        value: str | int | float
    ) -> Self:
        choice = cls(CommandChoicePayload(
            name=name,
            value=value
        ))

        assign_val(choice, {"name_localizations": name_localizations})

        return choice
    
    def _to_dict(self) -> CommandChoicePayload:
        return assign_val_dict(
            CommandChoicePayload(
                name=self.name,
                value=self.value
            ),
            {
                "name_localizations": mtd(self.name_localizations)
            }
        )

class ApplicationCommandOption:
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
        self.description_localizations = scls(Localization, data.get("description_localizations"))
        self.required = data.get("required", False)
        self.choices = [ApplicationCommandChoice(a) for a in data.get("choices", [])]
        self.options = [ApplicationCommandOption(a) for a in data.get("options", [])]
        self.channel_types = [ChannelType(c) for c in d] if (d := data.get("channel_types")) is not None else None
        self.min_value = data.get("min_value")
        self.max_value = data.get("max_value")
        self.min_length = data.get("min_length")
        self.max_length = data.get("max_length")
        self.autocomplete= data.get("autocomplete", False)

    @classmethod
    def new(
        cls, *,
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
        autocomplete: bool = False
    ) -> Self:
        return assign_val(
            cls(CommandOptionPayload(
                type=type.value,
                name=name,
                description=description,
                required=required,
                autocomplete=autocomplete
            )),
            {
                "name_localizations": name_localizations,
                "description_localizations": description_localizations,
                "choices": choices,
                "options": options,
                "channel_types": channel_types,
                "min_value": min_value,
                "max_value": max_value,
                "min_length": min_length,
                "max_length": max_length
            }
        )

    def _to_dict(self) -> CommandOptionPayload:
        return assign_val_dict(
            CommandOptionPayload(
                type=self.type.value,
                name=self.name,
                description=self.description,
                required=self.required,
                autocomplete=self.autocomplete
            ),
            {
                "name_localizations": mtd(self.name_localizations),
                "description_localizations": mtd(self.description_localizations),
                "choices": [c._to_dict() for c in self.choices] if self.choices else None,
                "options": [o._to_dict() for o in self.options] if self.options else None,
                "channel_types": [ct.value for ct in self.channel_types] if self.channel_types else None,
                "min_value": self.min_value,
                "max_value": self.max_value,
                "min_length": self.min_length,
                "max_length": self.max_length
            }
        )

type CoroFunc = Callable[..., Coroutine[Any, Any, Any]]

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
        self.description_localizations = scls(Localization, data.get("description_localizations"))
        self.options = [ApplicationCommandOption(a) for a in data.get("options", [])]
        self.nsfw = data.get("nsfw", False)
        self.integration_types = [ApplicationIntegrationType(a) for a in data.get("integration_types", [])]
        self.contexts = [InteractionContextType(i) for i in d] if (d := data.get("contexts")) is not None else None

class PartialApplicationCommand(BaseApplicationCommand):
    __slots__ = (
        "description",
        "default_member_permissions",
        "_callback"
    )
    
    def __init__(self, data: PartialApplicationCommandPayload, callback: CoroFunc | None):
        super().__init__(data)
        self.description = data.get("description")
        self.default_member_permissions = scls(Permissions, sint(data.get("default_member_permissions")))
        self._callback = callback

    @classmethod
    def new(
        cls, *,
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
        callback: CoroFunc = _MISSING
    ) -> Self:
        return assign_val(
            cls(PartialApplicationCommandPayload(
                name=name,
                type=type.value
            ), callback),
            {
                "name_localizations": name_localizations,
                "description": description,
                "description_localizations": description_localizations,
                "options": options,
                "default_member_permissions": default_member_permissions,
                "integration_types": integration_types,
                "contexts": contexts,
                "nsfw": nsfw
            }
        )

    def _to_dict(self) -> PartialApplicationCommandPayload:
        return assign_val_dict(
            PartialApplicationCommandPayload(
                name=self.name,
                type=self.type.value,
                nsfw=self.nsfw
            ),
            {
                "name_localizations": mtd(self.name_localizations),
                "description": self.description,
                "description_localizations": mtd(self.description_localizations),
                "options": [o._to_dict() for o in self.options] if self.options else None,
                "default_member_permissions": self.default_member_permissions.value if self.default_member_permissions else None,
                "integration_types": [i.value for i in self.integration_types] if self.integration_types else None,
                "contexts": [c.value for c in self.contexts] if self.contexts else None
            }
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