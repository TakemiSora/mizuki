from ..enums.channel import ChannelType
from ..enums.command import ApplicationCommandType, CommandHandler, CommandOptionType
from ..enums.interaction import ApplicationIntegrationType, InteractionContextTypes
from ..payloads.command import (
    ApplicationCommandPayload,
    CommandChoicePayload,
    CommandOptionPayload,
    LocalizationPayload,
)
from ..utils import scls
from .permissions import Permissions
from .snowflake import Snowflake

__all__ = (
    "Localization",
    "ApplicationCommandOption",
    "ApplicationCommandChoice",
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

class ApplicationCommandChoice:
    __slots__ = (
        "name",
        "name_localization",
        "value"
    )

    def __init__(self, data: CommandChoicePayload):
        self.name = data["name"]
        self.name_localization = scls(Localization, data.get("name_localizations"))
        self.value = data["value"]

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
        self.min_value = data.get("min__value")
        self.max_value = data.get("max_value")
        self.min_length = data.get("min_length")
        self.max_length = data.get("max_length")
        self.autocomplete= data.get("autocomplete", False)

class ApplicationCommand:
    __slots__ = (
        "id",
        "type",
        "application_id",
        "guild_id",
        "name",
        "name_localizations",
        "description",
        "description_localizations",
        "options",
        "default_member_permissions",
        "nsfw",
        "integration_types",
        "contexts",
        "version",
        "handler"
    )
    
    def __init__(self, data: ApplicationCommandPayload):
        self.id = Snowflake(data["id"])
        self.type = ApplicationCommandType(data.get("type", 1))
        self.application_id = Snowflake(data["application_id"])
        self.guild_id = Snowflake._from_str(data.get("guild_id"))
        self.name = data["name"]
        self.name_localizations = scls(Localization, data.get("name_localizations"))
        self.description = data["description"]
        self.description_localizations = scls(Localization, data.get("description_localizations"))
        self.options = [ApplicationCommandOption(a) for a in data.get("options", [])]
        self.default_member_permissions = scls(Permissions, data.get("default_member_permissions"))
        self.nsfw = data.get("nsfw", False)
        self.integration_types = [ApplicationIntegrationType(a) for a in data.get("integration_types", [])]
        self.contexts = [InteractionContextTypes(i) for i in d] if (d := data.get("contexts")) is not None else None
        self.version = Snowflake._from_str(data.get("version"))
        self.handler = scls(CommandHandler, data.get("handler"))